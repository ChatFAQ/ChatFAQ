from typing import Dict, List, Union

import ray
from pydantic import BaseModel
from ray import serve


@serve.deployment(
    name="llm_deployment",
    ray_actor_options={
        "num_cpus": 0.01,
        "resources": {
            "rags": 1,
        },
    },
)
class LLMDeployment:
    """
    Right now, this class is just a wrapper around a LLM client so it's a little overkill.
    We keep it like this to maintain the standard interface for all the AI components.
    """

    def __init__(
        self, llm_type: str, llm_name: str, base_url: str, model_max_length: int
    ):
        from chat_rag.llms import load_llm

        self.llm = load_llm(
            llm_type, llm_name, base_url=base_url, model_max_length=model_max_length
        )

    async def __call__(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        seed: int,
        tools: List[Union[BaseModel, Dict]] = None,
        tool_choice: str = None,
    ):
        if tools:  # LLM doesn't support tools in stream mode
            yield await self.llm.agenerate(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                seed=seed,
                tools=tools,
                tool_choice=tool_choice,
            )
        else:
            async for res in self.llm.astream(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                seed=seed,
            ):
                yield res

@ray.remote(num_cpus=0.1, resources={"tasks": 1})
def launch_llm_deployment(name: str, llm_type: str, llm_name: str, base_url: str = None, model_max_length: int = None, num_replicas: int = 1):
    from back.apps.language_model.ray_deployments import delete_serve_app

    # delete the deployment if it already exists
    task_name = f"delete_serve_app_{name}"
    print(f"Submitting the {task_name} task to the Ray cluster...")
    ray.get(delete_serve_app.options(name=task_name).remote(name))

    llm_app = LLMDeployment.options(
        name=name,
        num_replicas=num_replicas,
    ).bind(llm_type, llm_name, base_url, model_max_length)

    serve.run(llm_app, name=name, route_prefix=None)
