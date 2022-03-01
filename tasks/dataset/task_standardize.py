from clearml import Task, Dataset

PROJECT_NAME = "audio_preproc_test"
TASK_NAME = "audio_standardizing"
DATASET_POSTFIX = "_sd"
OUTPUT_URL = "s3://experiment-logging/storage"

task = Task.init(project_name=PROJECT_NAME, task_name=TASK_NAME)
task.set_base_docker(
    docker_image="python:3.8.12-slim-buster",
    docker_setup_bash_script= ['apt-get update', 'apt-get install -y sox libsox-fmt-all']
)

# librispeech_small dataset_task_id: 092896c34c0e45b598777222d9eaaee6
args = {
    'dataset_task_id': '',
    'input_filetype': '',
    'normalize': None,
    'sample_rate': None,
    'channels': None,
}

task.connect(args)
task.execute_remotely()

from preprocessing.standardize import Standardizer

# import dataset

dataset = Dataset.get(dataset_id = args['dataset_task_id'])
dataset_path = dataset.get_local_copy()

# process
standardizer = Standardizer(
    input_filetype = args['input_filetype'],
    normalize = args['normalize'],
    sample_rate = args['sample_rate'],
    channels = args['channels']    
)
new_dataset_path = standardizer(dataset_path)

# register ClearML Dataset
clearml_dataset = Dataset.create(
    dataset_project=dataset.project, dataset_name=dataset.name + DATASET_POSTFIX
)
clearml_dataset.add_files(new_dataset_path)
clearml_dataset.upload(output_url=OUTPUT_URL)
clearml_dataset.finalize()

print('Done')