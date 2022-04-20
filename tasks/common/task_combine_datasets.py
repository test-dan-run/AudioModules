# This script assumes that you have already generated train, dev, test manifests as artifacts for each dataset
from clearml import Task, Dataset, TaskTypes
from typing import List

#### PARAMS ####

PROJECT_NAME = "audio_preproc_test"
TASK_NAME = "combine_datasets"
DATASET_PROJECT = 'datasets/sample_dataset'
DATASET_NAME = 'test_audio_combined'
ARTIFACT_NAMES = ['train_manifest.json', 'dev_manifest.json', 'test_manifest.json']

# s3://<server url>:<port>/<bucket>/...
OUTPUT_URI = 's3://experiment-logging/storage'

################

task = Task.init(project_name=PROJECT_NAME, task_name=TASK_NAME, task_type=TaskTypes.data_processing)
task.set_base_docker(docker_image="dleongsh/audio_preproc:v1.0.0")

# librispeech_small dataset_task_id: 092896c34c0e45b598777222d9eaaee6
args = {
    'dataset_project': DATASET_PROJECT,
    'dataset_name': DATASET_NAME,
    'artifact_names': ARTIFACT_NAMES,
    'parent_dataset_ids': [],
}

task.connect(args)
task.execute_remotely()

# intialize dataset task as current task
dataset = Dataset.create(
    dataset_project = args['dataset_project'],
    dataset_name = args['dataset_name'],
    parent_datasets = args['parent_dataset_ids'],
)
dataset_task = Task.get_task(task_id=dataset.id)

# pull artifacts from each parent dataset
artifact_paths = {}

for parent_id in args['parent_dataset_ids']:
    parent_dataset_task = Task.get_task(task_id=parent_id)

    for artifact_name in args['artifact_names']:
        if artifact_name not in artifact_paths:
            artifact_paths[artifact_name] = []
        # pull artifact and store in a list
        artifact_path = parent_dataset_task.artifacts[artifact_name].get_local_copy()
        # if file does not exist
        if artifact_path is None:
            continue
        artifact_paths[artifact_name].append(artifact_path)

# combine and upload artifacts
for output_path in artifact_paths.keys():
    print(f'Combining {len(artifact_paths[output_path])} files into: {output_path}')
    with open(output_path, mode='w', encoding='utf-8') as fw:
        # enter each input artifact and append each line to the new output artifact
        for input_path in artifact_paths[output_path]:
            with open(input_path, mode='r', encoding='utf-8') as fr:
                lines = fr.readlines()
                for line in lines:
                    fw.write(line)

    # upload updated manifest as artifact
    dataset_task.upload_artifact(name = output_path, artifact_object = output_path)
    # upload updated manifest as file
    dataset.add_files(output_path)

# upload dataset to remote storage
dataset.upload(
    output_url=OUTPUT_URI, 
    verbose=True
)

# finalize the dataset
dataset.finalize()

task.set_parameter(
    name='output_dataset_id', 
    value=dataset.id, 
    description='the dataset task id of the output dataset',
) 

# end the task
task.close()
