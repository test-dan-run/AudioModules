from clearml import Task

def upload_model(
    project_name : str, 
    model_name: str, 
    local_model_path: str, 
    output_uri: str
    ) -> None:

    # initialize an empty task
    task = Task.init(
        project_name = project_name,
        task_name = model_name,
        output_uri = output_uri
    )

    # upload model as output model of the task
    task.update_output_model(
        model_path = local_model_path,
        name = model_name,
        model_name = model_name
    )

    # close the task
    task.close()
