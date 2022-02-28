# Standardizing audio files -> normalize, resampling, changing channels

import os
import shutil
import subprocess

def standardize(
    input_dir: str, input_filetype: str,  output_dir: str = 'temp',
    normalize: bool = True, sample_rate: int = 16000, channels: int = 1
    ) -> str:
    '''
    input_dir: the input directory
    input_filetype: audio filetype found in the audio input directory (".wav", ".mp3", etc.)
    output_dir: the output directory
    '''

    os.makedirs(output_dir, exist_ok=True)
    for root, _, files in os.walk(input_dir):
        for fx in files:
            # generate full output dir for the file
            output_fulldir = output_dir + root.replace(input_dir, '')
            os.makedirs(output_fulldir, exist_ok=True)

            input_path = root + '/' + fx

            # copy over non-audio files
            if not fx.endswith(input_filetype):            
                output_path = output_fulldir + '/' + fx
                shutil.copyfile(input_path, output_path)

            # use sox to resample, convert channel, and normalize
            else:
                output_path = output_fulldir + '/' + fx.replace(input_filetype, '.wav')

                sox_command = [
                    'sox', input_path, output_path, 
                    'channels', str(channels), 
                    'rate', str(sample_rate)
                    ]
                if normalize:
                    sox_command.extend(['norm', '-0.1']) # normalize to -0.1 dB sound level
                
                subprocess.run(sox_command)

    return output_dir

if __name__ == '__main__':

    # test
    LOCAL_DIR = '/home/daniel/datasets/mms2'
    OUTPUT_DIR = '/home/daniel/datasets/temp'

    standardize(LOCAL_DIR, OUTPUT_DIR)