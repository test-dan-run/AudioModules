from clearml import Task, StorageManager, Logger, Dataset

PROJECT_NAME = "xxx"
TASK_NAME = "audio_standardizing"

task = Task.init(project_name=PROJECT_NAME, task_name=TASK_NAME)
task.set_base_docker(
    docker_image="derekchia/cuda:11.5.1-cudnn8-runtime-ubuntu20.04",
    docker_setup_bash_script= ['apt-get update', 'apt-get install -y ffmpeg sox']
)

args = {
    'dataset_task_id': '',
    'sample_rate': '',
    'channels': '',
}

task.connect(args)
task.execute_remotely()

# xxx

from preprocessing.standardize import standardize

# yyy