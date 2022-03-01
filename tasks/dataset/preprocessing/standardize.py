# Standardizing audio files -> normalize, resampling, changing channels

import os
import shutil
import subprocess

class Standardizer():

    def __init__(
        self, input_filetype: str, 
        normalize: bool = True, sample_rate: int = 16000, channels: int = 1,
        ):
        '''
        input_filetype: audio filetype found in the audio input directory (".wav", ".mp3", etc.)
        '''
        self.input_filetype = input_filetype 
        self.normalize = normalize
        self.sample_rate = sample_rate
        self.channels = channels

    def standardize_audio(self, input_path: str, output_path: str) -> None:
        # use sox to resample, convert channel, and normalize
        sox_command = [
            'sox', input_path, output_path, 
            'channels', str(self.channels), 
            'rate', str(self.sample_rate)
            ]
        if self.normalize:
            sox_command.extend(['norm', '-0.1']) # normalize to -0.1 dB sound level
        
        subprocess.run(sox_command)

    def batch_standardize_audio(self, input_dir: str, output_dir: str) -> str:
        os.makedirs(output_dir, exist_ok=True)
        for root, _, files in os.walk(input_dir):
            for fx in files:
                # generate full output dir for the file
                output_fulldir = output_dir + root.replace(input_dir, '')
                os.makedirs(output_fulldir, exist_ok=True)

                input_path = root + '/' + fx

                # copy over non-audio files
                if not fx.endswith(self.input_filetype):            
                    output_path = output_fulldir + '/' + fx
                    shutil.copyfile(input_path, output_path)

                else:
                    output_path = output_fulldir + '/' + fx.replace(self.input_filetype, '.wav')
                    self.standardize_audio(input_path, output_path)

        return output_dir

    def __call__(self, input_dir: str, output_dir: str = 'temp'):
        return self.batch_standardize_audio(input_dir, output_dir)

if __name__ == '__main__':

    LOCAL_DIR = '/home/daniel/projects/AudioModules/test_audio'
    OUTPUT_DIR = '/home/daniel/projects/AudioModules/test_output'
    s = Standardizer(input_filetype='.wav', normalize=True, sample_rate=16000, channels=1)
    s(LOCAL_DIR, OUTPUT_DIR)