from clearml import Task, Dataset, TaskTypes
import shutil
import os

# PROJECT_NAME = "audio/speech_recognition"
# TASK_NAME = "audio_standardizing"
DATASET_POSTFIX = "-wav16k"
OUTPUT_URL = None

# task = Task.init(project_name=PROJECT_NAME, task_name=TASK_NAME, task_type=TaskTypes.data_processing)
# task.set_base_docker(docker_image="dleongsh/audio_preproc:v1.0.0")

# librispeech_small dataset_task_id: 092896c34c0e45b598777222d9eaaee6
args = {
    'dataset_task_id': '9653fcef34de44889f06f6342711e6c1',
    'manifest_path': 'test_manifest.json',
    'input_filetype': '.mp3',
    'normalize': True,
    'sample_rate': 16000,
    'channels': 1,
}

# task.connect(args)
# task.execute_remotely()

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
new_dataset_path, output_manifest_path = standardizer(dataset_path, manifest_path=args['manifest_path'])

# register ClearML Dataset
clearml_dataset = Dataset.create(
    dataset_project=dataset.project, dataset_name=dataset.name + DATASET_POSTFIX, parent_datasets=[args['dataset_task_id']],
)
clearml_dataset.sync_folder(new_dataset_path)
clearml_dataset.upload(output_url=OUTPUT_URL)

# upload manifest as artifact
clearml_dataset_task = Task.get_task(task_id=clearml_dataset.id)
clearml_dataset_task.upload_artifact(name=os.path.basename(output_manifest_path), artifact_object=output_manifest_path)

clearml_dataset.finalize()

# task.set_parameter(
#     name='output_dataset_id', 
#     value=clearml_dataset.id, 
#     description='the dataset task id of the output dataset',
# ) 

# task.close()

shutil.rmtree(new_dataset_path)
print('Done')
