from clearml.automation import PipelineController

# temporary placement of configs
RAW_DATASET_ID = "10b07eed06e642d3ab3589d399aa9833"
INPUT_FILETYPE = ".flac"
NORMALIZE = True
CHANNELS = 1
SAMPLE_RATE = 16000

MIN_SILENCE_LEN = 500
THRESH = 16

MAX_DURATION = 30000
MIN_DURATION = 5000

pipe = PipelineController(
    name="audio_preprocessing_pipeline",
    project="audio_preproc_test",
    version="0.0.1",
    add_pipeline_tags=True,
)

pipe.set_default_execution_queue("compute")

pipe.add_step(
    name="stage_standardizing",
    base_task_project="audio_preproc_test",
    base_task_name="audio_standardizing",
    parameter_override={
        "General/dataset_task_id": RAW_DATASET_ID,
        "General/input_filetype": INPUT_FILETYPE,
        "General/normalize": NORMALIZE,
        "General/channels": CHANNELS,
        "General/sample_rate": SAMPLE_RATE,
    }
)

pipe.add_step(
    name="stage_silence_splitting",
    parents=["stage_standardizing"],
    base_task_project="audio_preproc_test",
    base_task_name="audio_silence_split",
    parameter_override={
        "General/dataset_task_id": "${stage_standardizing.parameters.General/output_dataset_id}",
        "General/min_silence_len": MIN_SILENCE_LEN,
        "General/thresh": THRESH,
    }
)

pipe.add_step(
    name="stage_audio_splitting",
    parents=["stage_silence_splitting"],
    base_task_project="audio_preproc_test",
    base_task_name="audio_splitting",
    parameter_override={
        "General/dataset_task_id": "${stage_silence_splitting.parameters.General/output_dataset_id}",
        "General/max_duration": MAX_DURATION,
        "General/min_duration": MIN_DURATION,
    }
)

pipe.start()
print('Done')