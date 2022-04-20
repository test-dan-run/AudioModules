from tasks.local import upload_dataset

#### PARAMS ####

DATASET_PROJECT = 'datasets/sample_dataset'
DATASET_NAME = 'test_audio'
LOCAL_DATASET_DIR = '/home/daniel/projects/AudioModules/test_audio'
ARTIFACT_PATHS = ['/home/daniel/projects/AudioModules/test_audio/manifest.json',]

# s3://<server url>:<port>/<bucket>/...
OUTPUT_URI = 's3://experiment-logging/storage'

################

if __name__ == '__main__':

    upload_dataset(
        dataset_project = DATASET_PROJECT,
        dataset_name = DATASET_NAME,
        local_dataset_dir = LOCAL_DATASET_DIR,
        artifact_paths = ARTIFACT_PATHS,
        parent_ids = None,
        output_uri = OUTPUT_URI
    )
