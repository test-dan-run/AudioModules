from clearml import Task, StorageManager, Logger, Dataset

PROJECT_NAME = "audio_preproc_test"
TASK_NAME = "audio_standardizing"
DATASET_NAME = "librispeech_small_standardized"
OUTPUT_URL = "s3://experiment-logging/storage"

task = Task.init(project_name=PROJECT_NAME, task_name=TASK_NAME)
task.set_base_docker(
    docker_image="python:3.8.12-slim-buster",
    docker_setup_bash_script= ['apt-get update', 'apt-get install -y sox libsox-fmt-all']
)

args = {
    'dataset_task_id': '',
    'input_filetype': '',
    'normalize': None,
    'sample_rate': None,
    'channels': None,
}

task.connect(args)
task.execute_remotely()

from preprocessing.standardize import standardize

# import dataset

dataset = Dataset.get(dataset_id = args['dataset_task_id'])
dataset_path = dataset.get_local_copy()

# process
new_dataset_path = standardize(
    input_dir = dataset_path,
    input_filetype = args['input_filetype'],
    normalize = args['normalize'],
    sample_rate = args['sample_rate'],
    channels = args['channels']
)

# register ClearML Dataset
dataset = Dataset.create(
    dataset_project=PROJECT_NAME, dataset_name=DATASET_NAME
)
dataset.add_files(new_dataset_path)
dataset.upload(output_url=OUTPUT_URL)
dataset.finalize()

print('Done')

# yyy