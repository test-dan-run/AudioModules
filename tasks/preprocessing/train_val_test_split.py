import os
import json
import random
from typing import Iterable

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

        self.split_ratio = split_ratio
        self.split_names = split_names        
        random.seed(random_seed)

