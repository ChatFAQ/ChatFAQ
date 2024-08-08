import ray
from ray import serve


@ray.remote(num_cpus=0.1, resources={"tasks": 1})
def delete_serve_app(deployment_name: str):
    if serve.status().applications:
        serve.delete(deployment_name)
        try:
            serve.get_app_handle(deployment_name)
            # if it doesn't return error it means the deployment is still running
            print(
                f"{deployment_name} could not be deleted, so it doesn't exist or it is still running."
            )
        except Exception:
            print(f"{deployment_name} was deleted successfully")