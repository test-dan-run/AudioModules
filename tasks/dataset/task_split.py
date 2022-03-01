
from preprocessing.split import AudioSplitter
from clearml import Task, Dataset

PROJECT_NAME = "audio_preproc_test"
TASK_NAME = "audio_splitting"
DATASET_POSTFIX = '_split'

OUTPUT_URL = "s3://experiment-logging/storage"
# Task.add_requirements("requirements.txt")
Task.force_requirements_env_freeze(
    force=True, requirements_file='requirements.txt')
task = Task.init(project_name=PROJECT_NAME, task_name=TASK_NAME)

task.set_base_docker(
    docker_image="python:3.8",
    docker_setup_bash_script=['apt-get update',
                              'apt-get install -y sox libsox-fmt-all', 'apt install -y ffmpeg']
)

# librispeech_small dataset_task_id: 092896c34c0e45b598777222d9eaaee6
# test_audio dataset_task_id :  a1ecd57f6419c84110ebd7e24b55c72d83f1ee381567ae05c8b733ada82a9fd9
args = {
    'dataset_task_id': 'a1ecd57f6419c84110ebd7e24b55c72d83f1ee381567ae05c8b733ada82a9fd9',
    'min_duration': 5000,
    'max_duration': 30000,
}

task.connect(args)
task.execute_remotely()

dataset = Dataset.get(dataset_id=args['dataset_task_id'])
dataset_path = dataset.get_local_copy()
print('dataset path', dataset_path)

temp_path = '/tmp'
audio_splitter = AudioSplitter(args['min_duration'], args['max_duration'])
audio_splitter(dataset_path, '/tmp')


clearml_dataset = Dataset.create(
    dataset_project=dataset.project, dataset_name=dataset.name + DATASET_POSTFIX)
clearml_dataset.add_files(temp_path)
clearml_dataset.upload(output_url=OUTPUT_URL)
clearml_dataset.finalize()
print('Done')
