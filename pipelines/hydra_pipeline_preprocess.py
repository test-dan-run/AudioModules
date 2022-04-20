import ast
from typing import Dict, Any

from clearml import Task
from clearml.automation import PipelineController

import hydra
from omegaconf import OmegaConf

def get_clearml_params(task: Task) -> Dict[str, Any]:
    '''
    returns task params as a dictionary
    the values are casted in the required Python type
    '''
    string_params = task.get_parameters()
    clean_params = {}
    for k,v in string_params.items():
        try:
            # ast.literal eval cannot read empty strings + actual strings
            # i.e. ast.literal_eval("True") -> True, ast.literal_eval("i am cute") -> error
            clean_params[k] = ast.literal_eval(v)
        except:
            # if exception is triggered, it's an actual string, or empty string
            clean_params[k] = v
    return clean_params

def parse_stage_arguments(
    params: Dict[str, Any], 
    stage: str, 
    prefix: str = '/stages/',
    add_args: Dict[str, Any] = None) -> Dict[str, Any]:
    '''
    filters down the arguments into the only ones required for designated stage

    add_args: add additional arguments, useful when you pass values from previous steps
    '''
    filtered_args = {k:v for k, v in params.items() if stage in k}
    parsed_args = {k.replace(prefix+stage, ''):v for k,v in filtered_args.items()}
    # add additional arguments
    if add_args:
        parsed_args.update(add_args)

    return parsed_args

@hydra.main(config_path='configs', config_name='main')
def main(hydra_cfg):

    # START of using hydra configs
    pipe = PipelineController(
        project=hydra_cfg['controller']['project'],
        name=hydra_cfg['controller']['name'],
        version=hydra_cfg['controller']['version'],
        add_pipeline_tags=True
    )
    task = Task.current_task()
    task.connect(OmegaConf.to_container(hydra_cfg, resolve=True))
    pipe.set_default_execution_queue(hydra_cfg['default_task_queue'])

    # to set default docker image, set environment variable
    # export CLEARML_DOCKER_IMAGE=dleongsh/audio_preproc:v1.0.0

    # END of using hydra configs

    # PULL ClearML Params
    cfg = get_clearml_params(task)

    #### STEP 1 ####
    step1_args = parse_stage_arguments(
        params=cfg,
        stage='stage_standardizing',
    )
    step1_task_id = Task.get_task(
        project_name='audio_preproc_test', 
        task_name='audio_standardizing',
        task_filter={'status': ['published',]}
        ).id

    #### STEP 2 ####
    step2_args = parse_stage_arguments(
        params=cfg,
        stage='stage_silence_splitting',
        add_args={'General/dataset_task_id': '${stage_standardizing.parameters.General/output_dataset_id}'}
    )
    step2_task_id = Task.get_task(
        project_name='audio_preproc_test', 
        task_name='audio_silence_split',
        task_filter={'status': ['published',]}
        ).id

    #### STEP 3 ####
    step3_args = parse_stage_arguments(
        params=cfg,
        stage='stage_audio_splitting',
        add_args={'General/dataset_task_id': '${stage_silence_splitting.parameters.General/output_dataset_id}'}
    )
    step3_task_id = Task.get_task(
        project_name='audio_preproc_test', 
        task_name='audio_splitting',
        task_filter={'status': ['published',]}
        ).id
        
    #### STEP 4 ####
    step4_args = parse_stage_arguments(
        params=cfg,
        stage='stage_dataset_splitting',
        add_args={'General/dataset_task_id': '${stage_audio_splitting.parameters.General/output_dataset_id}'}
    )
    step4_task_id = Task.get_task(
        project_name='audio_preproc_test',
        task_name='dataset_split',
        task_filter={'status': ['published',]}
        ).id

    # add all pipeline steps
    pipe.add_step(
        name="stage_standardizing",
        base_task_id=step1_task_id,
        parameter_override=step1_args
    )
    pipe.add_step(
        name="stage_silence_splitting",
        base_task_id=step2_task_id,
        parents=["stage_standardizing",],
        parameter_override=step2_args
    )
    pipe.add_step(
        name="stage_audio_splitting",
        base_task_id=step3_task_id,
        parents=["stage_silence_splitting",],
        parameter_override=step3_args
    )
    pipe.add_step(
        name="stage_dataset_splitting",
        base_task_id=step4_task_id,
        parents=["stage_audio_splitting",],
        parameter_override=step4_args
    )


    pipe.start(queue=cfg['General/default_pipeline_queue'])
    print('Done')

if __name__ == '__main__':
    main()
