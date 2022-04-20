import os
from clearml import Task, Dataset
from typing import List

def upload_dataset(
    dataset_project: str, 
    dataset_name: str,
    local_dataset_dir: str,
    artifact_paths: List[str] = [], 
    parent_ids: List[str] = None,
    output_uri: str = None
    ) -> None:
    '''
    artifact_paths: local files into easily accessible clearml files that can be used via the web UI or programatically
    parent_ids: ids of parent datasets if wish to extend from existing parent datasets
    '''

    # initialize empty task
    task = Task.init(
        project_name = dataset_project, 
        task_name = dataset_name, 
        output_uri=output_uri,
        task_type='data_processing'
        )

    # add artifacts
    for artifact_path in artifact_paths:
        task.upload_artifact(
            name = os.path.basename(artifact_path), 
            artifact_object = artifact_path
        )

    # intialize dataset task as current task
    dataset = Dataset.create(
        dataset_project = dataset_project,
        dataset_name = dataset_name,
        parent_datasets = parent_ids,
        use_current_task = True
    )

    # add all files in the local directory
    dataset.add_files(local_dataset_dir)
    
    # upload dataset to remote storage
    dataset.upload(
        output_url=output_uri, 
        verbose=True
    )

    # finalize the dataset
    dataset.finalize()

    # end the task
    task.close()
