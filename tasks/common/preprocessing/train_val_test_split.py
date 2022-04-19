import os
import math
import json
import random
from typing import Iterable, List

class DatasetSplitter():
    def __init__(
        self, 
        split_ratio: Iterable[float] = (0.7, 0.2, 0.1), 
        split_names: Iterable[str] = ('train', 'dev', 'test'),
        random_seed: int = 42
        ) -> None:
        '''
        split_ratio: the ratio to split the datasets into
        split_names: the name of each split
        '''
        assert len(split_ratio) == len(split_names), \
             'no. of floats in split_ratio should correspond to the no. of names in split_names'

        assert math.fsum(split_ratio) == 1.0, 'split_ratio should sum up to 1'

        self.split_boundary = []
        for idx in range(len(split_ratio)):
            self.split_boundary.append(sum(split_ratio[:idx+1]))
        self.split_names = split_names        
        random.seed(random_seed)

    def split_manifest(
        self,
        input_manifest_path: str,
        ) -> List[str]:

        data_splits = [[] for _ in range(len(self.split_boundary))]
        with open(input_manifest_path, mode='r', encoding='utf-8') as f:

            lines = f.readlines()
            for line in lines:
                random_val = random.random()
                for idx, boundary in enumerate(self.split_boundary):
                    if random_val < boundary:
                        data_splits[idx].append(json.loads(line))
                        break
        
        file_paths = []
        for name, data_split in zip(self.split_names, data_splits):
            file_path = os.path.join(name + '_manifest.json')
            with open(file_path, mode='w', encoding='utf-8') as f:
                for item in data_split:
                    f.write(json.dumps(item) + '\n')

            file_paths.append(file_path)

        return file_paths


if __name__ == '__main__':
    INPUT_MANIFEST_PATH = '/home/daniel/datasets/emotion_sd/manifest.json'
    s = DatasetSplitter(split_ratio=(0.7, 0.2, 0.1), split_names=('train', 'dev', 'test'), random_seed=42)
    s.split_manifest(INPUT_MANIFEST_PATH)