from clearml import Task, Dataset

PROJECT_NAME = "audio_preproc_test"
TASK_NAME = "audio_silence_split"
DATASET_NAME = "librispeech_small_standardized"
OUTPUT_URL = "s3://experiment-logging/storage"

task = Task.init(project_name=PROJECT_NAME, task_name=TASK_NAME)
task.set_base_docker(
    docker_image="python:3.8.12-slim-buster",
    docker_setup_bash_script= [
        'apt-get update', 'apt-get install -y ffmpeg sox libsox-fmt-all', 
        'python3 -m pip install librosa pydub']
)

# librispeech_small dataset_task_id: 092896c34c0e45b598777222d9eaaee6
args = {
    'dataset_task_id': '',
    'manifest_path': 'manifest.json',
    'thresh': 16,
    'min_silence_len': 500,
}

task.connect(args)
task.execute_remotely()

from preprocessing.silence_split import batch_silence_split

# import dataset

dataset = Dataset.get(dataset_id = args['dataset_task_id'])
dataset_path = dataset.get_local_copy()

# process
new_dataset_path = batch_silence_split(
    input_dir = dataset_path,
    manifest_path = args['manifest_path'],
    thresh = args['thresh'],
    min_silence_len = args['min_silence_len']
)

# register ClearML Dataset
dataset = Dataset.create(
    dataset_project=PROJECT_NAME, dataset_name=DATASET_NAME
)
dataset.add_files(new_dataset_path)
dataset.upload(output_url=OUTPUT_URL)
dataset.finalize()

print('Done')