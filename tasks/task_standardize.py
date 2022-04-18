from clearml import Task, Dataset, TaskTypes

PROJECT_NAME = "audio_preproc_test"
TASK_NAME = "audio_standardizing"
DATASET_POSTFIX = "_sd"
OUTPUT_URL = "s3://experiment-logging/storage"

task = Task.init(project_name=PROJECT_NAME, task_name=TASK_NAME, task_type=TaskTypes.data_processing)
task.set_base_docker(docker_image="dleongsh/audio_preproc:v1.0.0")

# librispeech_small dataset_task_id: 092896c34c0e45b598777222d9eaaee6
args = {
    'dataset_task_id': '',
    'manifest_path': 'manifest.json',
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
new_dataset_path, output_manifest_path = standardizer(dataset_path, manifest_path=args['manifest_path'])

# upload manifest file as artifact
task.upload_artifact(name='manifest.json', artifact_object=output_manifest_path)

# register ClearML Dataset
clearml_dataset = Dataset.create(
    dataset_project=dataset.project, dataset_name=dataset.name + DATASET_POSTFIX
)
clearml_dataset.add_files(new_dataset_path)
clearml_dataset.upload(output_url=OUTPUT_URL)
clearml_dataset.finalize()

task.set_parameter(
    name='output_dataset_id', 
    value=clearml_dataset.id, 
    description='the dataset task id of the output dataset'
    ) 
print('Done')
