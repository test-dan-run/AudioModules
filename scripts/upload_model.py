from tasks.local import upload_model

#### PARAMS ####

PROJECT_NAME = 'example_projects/pretrained_models'
MODEL_NAME = 'example_model_v1.0'

# s3://<server url>:<port>/<bucket>/...
OUTPUT_URI = 's3://min.io:80/clearml-data/default'
LOCAL_MODEL_PATH = '/mnt/d/pretrained_models/example_model.ckpt'

################

if __name__ == '__main__':

    upload_model(
        project_name = PROJECT_NAME,
        model_name = MODEL_NAME,
        local_model_path = LOCAL_MODEL_PATH,
        output_uri = OUTPUT_URI
    )
