
from clearml import Task, Dataset, TaskTypes

PROJECT_NAME = "audio_preproc_test"
TASK_NAME = "audio_splitting"
DATASET_POSTFIX = '_split'
OUTPUT_URL = "s3://experiment-logging/storage"

task = Task.init(project_name=PROJECT_NAME, task_name=TASK_NAME, task_type=TaskTypes.data_processing)
task.set_base_docker(docker_image="dleongsh/audio_preproc:v1.0.0")

args = {
    'dataset_task_id': '',
    'min_duration': 5000,
    'max_duration': 30000,
}

task.connect(args)
task.execute_remotely()

from preprocessing import DurationSplitter

dataset = Dataset.get(dataset_id=args['dataset_task_id'])
dataset_path = dataset.get_local_copy()
print('dataset path', dataset_path)

temp_path = '/output_data'
audio_splitter = DurationSplitter(args['min_duration'], args['max_duration'])
audio_splitter(dataset_path, temp_path)


clearml_dataset = Dataset.create(
    dataset_project=dataset.project, dataset_name=dataset.name + DATASET_POSTFIX)
clearml_dataset.add_files(temp_path)
clearml_dataset.upload(output_url=OUTPUT_URL)
clearml_dataset.finalize()

task.set_parameter(
    name="output_dataset_id", 
    value=clearml_dataset.id, 
    description="the dataset task id of the output dataset"
    ) 
print('Done')
