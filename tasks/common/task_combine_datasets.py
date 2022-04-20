# This script assumes that you have already generated train, dev, test manifests as artifacts for each dataset
import os
from clearml import Task, Dataset
from typing import List

#### PARAMS ####

DATASET_PROJECT = 'datasets/sample_dataset'
DATASET_NAME = 'test_audio_combined'
ARTIFACT_NAMES = ['train_manifest.json', 'dev_manifest.json', 'test_manifest.json']

# s3://<server url>:<port>/<bucket>/...
OUTPUT_URI = 's3://experiment-logging/storage'

################

def combine_datasets(
    dataset_project: str, 
    dataset_name: str,
    artifact_names: List[str] = [], 
    parent_ids: List[str] = None,
    output_uri: str = None
    ) -> None:
    '''
    artifact_names: Names of artifacts to combine (assume they have the same name across datasets)
    parent_ids: ids of datasets to combine with
    '''

    # initialize empty task
    task = Task.init(
        project_name = dataset_project, 
        task_name = dataset_name, 
        output_uri=output_uri,
        task_type='data_processing'
        )

    # intialize dataset task as current task
    dataset = Dataset.create(
        dataset_project = dataset_project,
        dataset_name = dataset_name,
        parent_datasets = parent_ids,
        use_current_task = True
    )

    # pull artifacts from each parent dataset
    artifact_paths = {}

    for parent_id in parent_ids:
        parent_dataset_task = Task.get_task(task_id=parent_id)

        for artifact_name in artifact_names:
            if artifact_name not in artifact_paths:
                artifact_paths[artifact_name] = []
            # pull artifact and store in a list
            artifact_paths[artifact_name].append(
                parent_dataset_task.artifacts[artifact_name].get_local_copy()
            )

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
        task.upload_artifact(name = output_path, artifact_object = output_path)
        # upload updated manifest as file
        dataset.add_files(output_path)

    # upload dataset to remote storage
    dataset.upload(
        output_url=output_uri, 
        verbose=True
    )

    # finalize the dataset
    dataset.finalize()

    # end the task
    task.close()

if __name__ == '__main__':

    combine_datasets(
        dataset_project = DATASET_PROJECT,
        dataset_name = DATASET_NAME,
        artifact_names = ARTIFACT_NAMES,
        parent_ids = None,
        output_uri = OUTPUT_URI
    )