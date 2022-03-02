# Standardizing audio files -> normalize, resampling, changing channels

import os
import json
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

    def batch_standardize_audio(self, input_dir: str, output_dir: str, manifest_path: str) -> str:
        os.makedirs(output_dir, exist_ok=True)
        with open(os.path.join(input_dir, manifest_path), mode='r', encoding='utf-8') as fr, \
            open(os.path.join(output_dir, manifest_path), mode='w', encoding='utf-8') as fw:

            for idx, line in enumerate(fr.readlines()):
                if idx % 100 == 0 and idx != 0:
                    print(f'no. of files processed: {idx}')
                d = json.loads(line)
                relative_input_path = d['audio_filepath']
                os.makedirs(os.path.join(output_dir, os.path.dirname(d['audio_filepath'])), exist_ok=True)

                full_input_path = os.path.join(input_dir, relative_input_path)
                relative_output_path = relative_input_path.replace(self.input_filetype, '.wav')
                full_output_path = os.path.join(output_dir, relative_output_path)

                self.standardize_audio(full_input_path, full_output_path)
                d['audio_filepath'] = relative_output_path
                fw.write(json.dumps(d) + '\n')

        print('total no. of files processed:', idx+1)
        return output_dir

    def __call__(self, input_dir: str, output_dir: str = 'temp', manifest_path: str = 'manifest.json'):
        return self.batch_standardize_audio(input_dir, output_dir, manifest_path)

if __name__ == '__main__':

    LOCAL_DIR = '/home/daniel/projects/AudioModules/test_audio'
    OUTPUT_DIR = '/home/daniel/projects/AudioModules/test_output'
    s = Standardizer(input_filetype='.wav', normalize=True, sample_rate=16000, channels=1)
    s(LOCAL_DIR, OUTPUT_DIR)