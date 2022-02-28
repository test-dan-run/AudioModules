import os
import json
import librosa
from typing import List
from pydub import AudioSegment
from pydub.silence import split_on_silence

def silence_split(path: str, thresh: int, min_silence_len: int) -> List[AudioSegment]:
    '''
    path: string path to the audio file
    thresh: the silence threshold according to decibels relative to full scale (dBFS)
    min_silence_len: The minimum length of silence before splitting (in ms)
    '''
    audio = AudioSegment.from_wav(path)
    # decibels relative to full scale
    dBFS = audio.dBFS
    silence_thresh = dBFS - thresh
    chunks = split_on_silence(
        audio,
        min_silence_len = min_silence_len,
        silence_thresh = silence_thresh
    )

    return chunks

def batch_silence_split(
    input_dir: str, output_dir: str = 'temp', manifest_path: str = 'manifest.json', 
    thresh: int = 16, min_silence_len: int = 500
    ) -> str:
    '''
    input_dir: the input directory
    output_dir: the output directory
    manifest_path: path to manifest file from the input_dir
    thresh: the silence threshold according to decibels relative to full scale (dBFS)
    min_silence_len: The minimum length of silence before splitting (in ms)
    '''
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(input_dir, manifest_path), mode='r', encoding='utf-8') as fr, \
        open(os.path.join(output_dir, manifest_path), mode='w', encoding='utf-8') as fw:

        for line in fr.readlines():
            d = json.loads(line)
            orig_path = d['audio_filepath']
            os.makedirs(os.path.join(output_dir, os.path.dirname(d['audio_filepath'])), exist_ok=True)

            audio_chunks = silence_split(
                path = os.path.join(input_dir, orig_path), 
                thresh=thresh, min_silence_len=min_silence_len
                )
            for idx, chunk in enumerate(audio_chunks):
                chunk_path = orig_path.replace('.wav', f'_{str(idx)}.wav')

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

    return output_dir

if __name__ == '__main__':

    LOCAL_DIR = '/home/daniel/projects/AudioModules/test_audio'
    OUTPUT_DIR = '/home/daniel/projects/AudioModules/test_output'
    batch_silence_split(LOCAL_DIR, OUTPUT_DIR)

