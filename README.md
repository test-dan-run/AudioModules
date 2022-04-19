# AudioModules
A repository of tasks and pipelines to preprocess audio files for ML pipelines. The repository is centered around the ClearML MLOps Framework.

## Getting Started
### Via local environment (linux)
1. Ensure that you have the following apt packages installed
```shell
apt-get update && apt-get install libsndfile1 ffmpeg sox libsox-fmt-all
```

2. Create a local python environment and install the packages in the `requirements.txt`
```shell
python3 -m venv audiomodules
source audiomodules/bin/activate
python3 -m pip install -r requirements.txt
```
### Via Docker
We have already created a dockerfile with the required apt and python packages. Simply build it via the following command:
```shell
docker build -t audiomodules:latest .
```

## Project Organization

    ├── README.md          <- The top-level README for developers using this project.
    ├── tasks
    |   ├── audio <- audio modules
    |   │   ├── preprocessing           <- individual scripts to preprocess data
    |   |   │   ├── silence_split.py
    |   |   │   ├── split.py
    |   |   │   └── standardize.py
    |   |   ├── task_silence_split.py   <- ClearML-wrapped preproc scripts
    |   |   ├── task_split.py
    |   |   └── task_standardize.py
    |   |    
    |   ├── common
    |       ├── preprocessing           <- individual scripts to preprocess data
    |       │   ├── generate_manifest.py
    |       │   └── train_val_test_split.py
    |       ├── task_generate_manifest.py   <- ClearML-wrapped preproc scripts
    |       ├── task_train_val_test_split.py
    |       ├── task_upload_dataset.py
    |       └── task_upload_model.py
    |
    ├── pipelines
    |   ├── configs        <- Hydra config folder
    |   |   └── main.yaml
    |   ├── pipeline_preprocess.py  <- ClearML pipeline script to run preproc tasks
    |   └── hydra_pipeline_preprocess.py <- Hydra-wrapped ClearML pipeline
    │
    ├── dockerfile         <- The dockerfile to build an image with the required packages
    │
    └── requirements.txt   <- The requirements file for reproducing project environment


## Available Modules
### Standardize
Standardizes all of the files in the input directory by normalization, sampling rate, and number of channels.

**Arguments**
- `input_filetype`: (str) the audio filetype found in the audio input directory (".wav", ".mp3", etc.)
- `normalize`: (bool) whether to normalize the audio by each file's maximum volume
- `sample_rate`: (int) the value to upsample/downsample to
- `channels`: (int) the number of channels to convert to

### Silence Split
Splits audio, with silence as the separator. 

**Arguments**
- `thresh`: (int) how many decibels below the maximum volume (relative to full scale) before we determine if it's a silence or not (threshold)
- `min_silence_len`: (int) how many milliseconds of silence before we start slicing

### Audio Split
Splits audio if a given audio file is too long.

**Arguments**
- `max_duration`: (int) the maximum length of an audio file, otherwise split.
- `min_duration`: (int) ensures the split audio file is not shorter than this min duration

## How to Use

### Run Individual Tasks
Configure the parameters at the top of each script, then run the python scripts. 

### Run Pipelines

**Non-Hydra Pipeline**
- Configure the parameters at the top of the pipeline script, then run the pipeline script.
```shell
cd pipelines
python3 pipeline_preprocess.py
```

**Hydra Pipeline**
- Configure the parameters in the `configs/main.yaml` file, then run the hydra pipeline script.
```shell
cd pipelines
python3 hydra_pipeline_preprocess.py
```