# Standardizing audio files -> normalize, resampling, changing channels

import os
import json
from pathlib import Path
import audiosegment
from pydub.utils import make_chunks


class AudioSplitter():

    def __init__(self, min_duration: int, max_duration: int):
        '''
        in milliseconds
        '''
        self.max_duration = max_duration
        self.min_duration = min_duration

    def __call__(self, original_path: str, processed_path: str) -> None:
        with open(os.path.join(original_path, 'manifest.json')) as f:
            manifest = f.readlines()

        new_manifest = []
        for item_string in manifest:
            item = json.loads(item_string)

            original_path = Path(original_path)
            processed_path = Path(processed_path)
            # Replicating directory in sets
            full_file_path = os.path.join(
                original_path, item['audio_filepath'])
            full_folder_location = str(Path(full_file_path).parent)

            print(full_file_path)

            new_folder_location = full_folder_location.replace(
                str(original_path), str(processed_path))

            print(new_folder_location)

            os.makedirs(new_folder_location, exist_ok=True)

            sound = audiosegment.from_file(full_file_path)

            og_name = Path(full_file_path).stem

            duration = len(sound)

            if (duration < self.max_duration):
                sound.export(os.path.join(
                    new_folder_location, og_name), format="wav")
                new_manifest.append(item)
                print("Export completed successfully.")
            else:
                old_file_path = Path(item['audio_filepath'])
                remainder = duration % self.max_duration
                if (remainder < self.min_duration):
                    sound = sound[:duration-remainder]
                chunks = make_chunks(sound, self.max_duration)
                for i, chunk in enumerate(chunks):

                    chunk_name = f'{og_name}-{str(i+1)}.wav'
                    print("exporting ", chunk_name)
                    # Save chunk to specific folder
                    chunk.export(os.path.join(new_folder_location,
                                 chunk_name), format="wav")

                    item['audio_filepath'] = os.path.join(
                        str(old_file_path.parent), chunk_name)
                    new_manifest.append(item)
        with open(os.path.join(str(processed_path), 'manifest.json'), 'a') as f:
            for item in new_manifest:
                json.dump(item, f)

    

if __name__ == '__main__':

    a = AudioSplitter(3000, 30000)
    a('/AudioModules/test_audio/', '/tmp')
