import os
import json
import librosa
from typing import List
from pydub import AudioSegment
from pydub.silence import split_on_silence

class SilenceSplitter():
    def __init__(self, thresh: int = 16, min_silence_len: int = 500) -> None:
        '''
        thresh: the silence threshold according to decibels relative to full scale (dBFS)
        min_silence_len: The minimum length of silence before splitting (in ms)
        '''
        self.thresh = thresh
        self.min_silence_len = min_silence_len

    def silence_split(self, path: str) -> List[AudioSegment]:
        '''
        path: string path to the audio file
        '''
        audio = AudioSegment.from_wav(path)
        # decibels relative to full scale
        dBFS = audio.dBFS
        silence_thresh = dBFS - self.thresh
        chunks = split_on_silence(
            audio,
            min_silence_len = self.min_silence_len,
            silence_thresh = silence_thresh
        )

        return chunks

    def batch_silence_split(self, input_dir: str, output_dir: str, manifest_path: str) -> str:
        '''
        input_dir: the input directory
        output_dir: the output directory
        manifest_path: path to manifest file from the input_dir
        thresh: the silence threshold according to decibels relative to full scale (dBFS)
        min_silence_len: The minimum length of silence before splitting (in ms)
        '''
        os.makedirs(output_dir, exist_ok=True)
        print('Batch processing of silence splits...')
        with open(os.path.join(input_dir, manifest_path), mode='r', encoding='utf-8') as fr, \
            open(os.path.join(output_dir, manifest_path), mode='w', encoding='utf-8') as fw:
            total_num_chunks = 0

            for idx, line in enumerate(fr.readlines()):
                if idx % 100 == 0 and idx != 0:
                    print(f'no. of files processed: {idx}')
                d = json.loads(line)
                orig_path = d['audio_filepath']
                os.makedirs(os.path.join(output_dir, os.path.dirname(d['audio_filepath'])), exist_ok=True)

                audio_chunks = self.silence_split(os.path.join(input_dir, orig_path))
                total_num_chunks += len(audio_chunks)
                for chunk_idx, chunk in enumerate(audio_chunks):
                    chunk_path = orig_path.replace('.wav', f'_{str(chunk_idx)}.wav')

                    # export the chunk as a wav file
                    chunk.export(
                        os.path.join(output_dir, chunk_path),
                        format = 'wav'
                    )
                    # replace audio_filepath with chunk path, and its length
                    d['audio_filepath'] = chunk_path
                    d['duration'] = round(
                        librosa.get_duration(filename=os.path.join(output_dir, chunk_path)), 3)
                    fw.write(json.dumps(d) + '\n')

        print('total no. of files processed:', idx+1)
        print('total no. of files produced:', total_num_chunks)
        
        # returns dataset dir and new manifest file path
        return output_dir, os.path.join(output_dir, manifest_path)

    def __call__(self, input_dir: str, output_dir: str = 'temp', manifest_path: str = 'manifest.json'):
        return self.batch_silence_split(input_dir, output_dir, manifest_path)

if __name__ == '__main__':

    LOCAL_DIR = '/home/daniel/projects/AudioModules/test_audio'
    OUTPUT_DIR = '/home/daniel/projects/AudioModules/test_output'
    s = SilenceSplitter(thresh=16, min_silence_len=500)
    s(LOCAL_DIR, OUTPUT_DIR)