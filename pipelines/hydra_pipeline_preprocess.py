from clearml import Task, TaskTypes
from clearml.config import running_remotely
from typing import Dict, Any
from clearml.automation import PipelineController
import hydra
from omegaconf import OmegaConf

def parse_stage_arguments(params: Dict[str, Any], stage: str, prefix: str = 'stages/'):
    filtered_args = {k:v for k, v in params.items() if stage in k}
    parsed_args = {k.replace(prefix+stage, ''):v for k,v in filtered_args.items()}
    return parsed_args

@hydra.main(config_path='configs', config_name='main')
def main(hydra_cfg):

    task = Task.init(
        project_name=hydra_cfg['controller']['project'],
        task_name=hydra_cfg['controller']['name'],
        task_type=TaskTypes.controller
    )
    if not running_remotely():
        # only connect config on remote launch
        task.connect(OmegaConf.to_container(hydra_cfg, resolve=True))
        task.set_base_docker('dleongsh/audio_preproc:v1.0.0')
        task.execute_remotely()

    cfg = {k.replace('General/', ''):v for k, v in task.get_parameters(cast=True).items()}
    if cfg['test']: 
        print('Stupiak! It doesn\'t work!')
        return

    else:
        print('Omg!? it works!?')

    pipe = PipelineController(
        project=cfg['General/controller/project'],
        name=cfg['General/controller/name'],
        version=cfg['General/controller/version'],
        add_pipeline_tags=True
    )
    pipe.set_default_execution_queue(cfg['default_queue'])

    pipe.add_step(
        name="stage_standardizing",
        base_task_project="default_tasks/audio_preproc_test",
        base_task_name="audio_standardizing",
        parameter_override=parse_stage_arguments(cfg, 'stage_standardizing')
    )

    pipe.add_step(
        name="stage_silence_splitting",
        parents=["stage_standardizing"],
        base_task_project="default_tasks/audio_preproc_test",
        base_task_name="audio_silence_split",
        parameter_override=parse_stage_arguments(cfg, 'stage_silence_splitting')
    )

    pipe.add_step(
        name="stage_audio_splitting",
        parents=["stage_silence_splitting"],
        base_task_project="default_tasks/audio_preproc_test",
        base_task_name="audio_splitting",
        parameter_override=parse_stage_arguments(cfg, 'stage_audio_splitting')
    )

    pipe.start()
    print('Done')

if __name__ == '__main__':
    main()