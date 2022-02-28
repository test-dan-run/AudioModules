from clearml import Task, StorageManager, Logger, Dataset

PROJECT_NAME = "xxx"
TASK_NAME = "audio_standardizing"

task = Task.init(project_name=PROJECT_NAME, task_name=TASK_NAME)
task.set_base_docker(
    docker_image="python:3.8.12-slim-buster",
    docker_setup_bash_script= ['apt-get update', 'apt-get install -y sox libsox-fmt-all']
)

args = {
    'dataset_task_id': '',
    'sample_rate': None,
    'channels': None,
    'normalize': None,
}

task.connect(args)
task.execute_remotely()

# xxx

from preprocessing.standardize import standardize

# yyy