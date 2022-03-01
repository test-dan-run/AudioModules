from clearml import Task, Dataset, TaskTypes

PROJECT_NAME = "audio_preproc_test"
TASK_NAME = "audio_silence_split"
DATASET_POSTFIX = "_sil"
OUTPUT_URL = "s3://experiment-logging/storage"

task = Task.init(project_name=PROJECT_NAME, task_name=TASK_NAME, task_type=TaskTypes.data_processing)
task.set_base_docker(
    docker_image="python:3.8.12-slim-buster",
    docker_setup_bash_script= [
        'apt-get update', 'apt-get install -y ffmpeg sox libsox-fmt-all', 
        'python3 -m pip install librosa pydub numpy==1.21.0']
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

from preprocessing.silence_split import SilenceSplitter

# import dataset

dataset = Dataset.get(dataset_id = args['dataset_task_id'])
dataset_path = dataset.get_local_copy()

# process
silence_splitter = SilenceSplitter(
    thresh = args['thresh'],
    min_silence_len = args['min_silence_len']
)

new_dataset_path = silence_splitter(
    input_dir = dataset_path,
    manifest_path = args['manifest_path'],
)

# register ClearML Dataset
clearml_dataset = Dataset.create(
    dataset_project=dataset.project, dataset_name=dataset.name + DATASET_POSTFIX
)
clearml_dataset.add_files(new_dataset_path)
clearml_dataset.upload(output_url=OUTPUT_URL)
clearml_dataset.finalize()

print('Done')