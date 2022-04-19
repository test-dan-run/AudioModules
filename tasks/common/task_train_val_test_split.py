from clearml import Task, Dataset, TaskTypes

PROJECT_NAME = "audio_preproc_test"
TASK_NAME = "dataset_split"
DATASET_POSTFIX = "_ds"
OUTPUT_URL = "s3://experiment-logging/storage"

task = Task.init(project_name=PROJECT_NAME, task_name=TASK_NAME, task_type=TaskTypes.data_processing)
task.set_base_docker(docker_image="dleongsh/audio_preproc:v1.0.0")

# librispeech_small dataset_task_id: 092896c34c0e45b598777222d9eaaee6
args = {
    'dataset_task_id': '',    
    'split_names': ('train', 'dev', 'test'),
    'split_ratio': (0.8, 0.1, 0.1),
    'random_seed': 42
}

task.connect(args)
task.execute_remotely()

import os
from preprocessing import DatasetSplitter

# import parent dataset's manifest file
parent_dataset = Dataset.get(dataset_id = args['dataset_task_id'])
input_manifest_path = parent_dataset.artifacts['manifest.json'].get_local_copy()

# initialize class object
ds_splitter = DatasetSplitter(
    split_ratio=args['split_ratio'],
    split_names=args['split_names'],
    random_seed=args['random_seed']
)

# run splitter
output_manifest_paths = ds_splitter.split_manifest(input_manifest_path=input_manifest_path)

# register ClearML Dataset
clearml_dataset = Dataset.create(
    dataset_project=parent_dataset.project, 
    dataset_name=parent_dataset.name + DATASET_POSTFIX, 
    parent_datasets=[args['dataset_task_id'],],
)

clearml_dataset_task = Task.get_task(task_id=clearml_dataset.id)

for path in output_manifest_paths:
    # upload each individual manifest file
    clearml_dataset.add_files(path)
    # upload manifest file as artifact
    clearml_dataset_task.upload_artifact(name=os.path.basename(path), artifact_object=path)

clearml_dataset.upload(output_url=OUTPUT_URL)
clearml_dataset.finalize()

task.set_parameter(
    name='output_dataset_id', 
    value=clearml_dataset.id, 
    description='the dataset task id of the output dataset'
    ) 
print('Done')
