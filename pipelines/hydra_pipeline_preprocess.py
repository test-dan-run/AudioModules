from clearml import Task, TaskTypes
from clearml.automation import PipelineController
import hydra
from omegaconf import OmegaConf

@hydra.main(config_path='configs', config_name='main')
def main(hydra_cfg):

    task = Task.init(
        project_name=hydra_cfg['controller']['project'],
        task_name=hydra_cfg['controller']['name'],
        task_type=TaskTypes.controller
    )

    task.connect(OmegaConf.to_container(hydra_cfg, resolve=True))
    cfg = {k.replace('General/', ''):v for k, v in task.get_parameters().items()}
    if cfg['test']: 
        'Stupiak! It doesn\'t work!'
        return

    pipe = PipelineController(
        project=cfg['controller']['project'],
        name=cfg['controller']['name'],
        version=cfg['controller']['version'],
        add_pipeline_tags=True
    )
    pipe.set_default_execution_queue(cfg['default_queue'])

    step1_cfg = cfg['stages']['stage_standardizing']
    pipe.add_step(
        name="stage_standardizing",
        base_task_project="default_tasks/audio_preproc_test",
        base_task_name="audio_standardizing",
        parameter_override={
            "General/dataset_task_id": step1_cfg['raw_dataset_id'],
            "General/input_filetype": step1_cfg['input_filetype'],
            "General/normalize": step1_cfg['normalize'],
            "General/channels": step1_cfg['channels'],
            "General/sample_rate": step1_cfg['sample_rate'],
        }
    )

    step2_cfg = cfg['stages']['stage_silence_splitting']
    pipe.add_step(
        name="stage_silence_splitting",
        parents=["stage_standardizing"],
        base_task_project="default_tasks/audio_preproc_test",
        base_task_name="audio_silence_split",
        parameter_override={
            "General/dataset_task_id": "${stage_standardizing.parameters.General/output_dataset_id}",
            "General/min_silence_len": step2_cfg['min_silence_len'],
            "General/thresh": step2_cfg['thresh'],
        }
    )

    step3_cfg = cfg['stages']['stage_audio_splitting']
    pipe.add_step(
        name="stage_audio_splitting",
        parents=["stage_silence_splitting"],
        base_task_project="default_tasks/audio_preproc_test",
        base_task_name="audio_splitting",
        parameter_override={
            "General/dataset_task_id": "${stage_silence_splitting.parameters.General/output_dataset_id}",
            "General/max_duration": step3_cfg['max_duration'],
            "General/min_duration": step3_cfg['min_duration'],
        }
    )

    pipe.start()
    print('Done')

if __name__ == '__main__':
    main()