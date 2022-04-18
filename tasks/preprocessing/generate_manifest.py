import os
import json
import librosa

class SimpleManifestGenerator():
    def __init__(self) -> None:
        '''
        this is just a template manifest generator
        you will have to add in other params of interest on your own
        '''
        pass

    def generate_manifest(self, data_dir: str, output_manifest_path: str = 'manifest.json') -> str:

        with open(output_manifest_path, mode='w', encoding='utf-8') as fw:
            for root, _, filenames in os.walk(data_dir):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    relative_filepath = os.path.relpath(filepath, data_dir)

                    duration = round(librosa.get_duration(filename=filepath), 2)

                    item = {
                        'audio_filepath': relative_filepath,
                        'duration': duration,
                        # add other params of interest here
                    }

                    fw.write(
                        json.dumps(item) + '\n'
                    )

        return output_manifest_path

if __name__ == '__main__':
    INPUT_DATA_DIR = '/home/daniel/datasets/emotion'
    generator = SimpleManifestGenerator()
    generator.generate_manifest(data_dir=INPUT_DATA_DIR)