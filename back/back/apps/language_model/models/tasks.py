from django.db import models
from ray.util.state import api as ray_api


class RayTaskState(models.Model):

    """
    This model represents the state of a parse task.
    It's intended to imitate a ray task state: https://docs.ray.io/en/latest/ray-observability/reference/doc/ray.util.state.common.TaskState.html#ray.util.state.common.TaskState
    """

    STATE_CHOICES = [
        ('NIL', 'NIL'),
        ('PENDING_ARGS_AVAIL', 'PENDING_ARGS_AVAIL'),
        ('PENDING_NODE_ASSIGNMENT', 'PENDING_NODE_ASSIGNMENT'),
        ('PENDING_OBJ_STORE_MEM_AVAIL', 'PENDING_OBJ_STORE_MEM_AVAIL'),
        ('PENDING_ARGS_FETCH', 'PENDING_ARGS_FETCH'),
        ('SUBMITTED_TO_WORKER', 'SUBMITTED_TO_WORKER'),
        ('RUNNING', 'RUNNING'),
        ('RUNNING_IN_RAY_GET', 'RUNNING_IN_RAY_GET'),
        ('RUNNING_IN_RAY_WAIT', 'RUNNING_IN_RAY_WAIT'),
        ('FINISHED', 'FINISHED'),
        ('FAILED', 'FAILED')
    ]
    STATE_CHOICES_DICT = {state[0]: state[1] for state in STATE_CHOICES}

    task_id = models.CharField(max_length=255, primary_key=True)
    attempt_number = models.IntegerField(default=1)
    name = models.CharField(max_length=255)
    state = models.CharField(max_length=255, choices=STATE_CHOICES, default='NIL')
    job_id = models.CharField(max_length=255, blank=True, null=True)
    actor_id = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, default='PARSE_TASK')
    func_or_class_name = models.CharField(max_length=255)
    parent_task_id = models.CharField(max_length=255, blank=True, null=True)
    node_id = models.CharField(max_length=255, blank=True, null=True)
    worker_id = models.CharField(max_length=255, blank=True, null=True)
    worker_pid = models.IntegerField(blank=True, null=True)
    error_type = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=255, blank=True, null=True)
    required_resources = models.JSONField(blank=True, null=True)
    runtime_env_info = models.JSONField(blank=True, null=True)
    placement_group_id = models.CharField(max_length=255, blank=True, null=True)
    events = models.JSONField(blank=True, null=True)
    profiling_data = models.JSONField(blank=True, null=True)
    creation_time_ms = models.IntegerField(blank=True, null=True)
    start_time_ms = models.IntegerField(blank=True, null=True)
    end_time_ms = models.IntegerField(blank=True, null=True)
    task_log_info = models.JSONField(blank=True, null=True)
    error_message = models.CharField(max_length=255, blank=True, null=True)
    is_debugger_paused = models.BooleanField(blank=True, null=True)

    @classmethod
    def get_all_ray_and_parse_tasks_serialized(cls):
        from back.apps.language_model.serializers.tasks import RayTaskStateSerializer

        parse_task_states = cls.objects.all()

        parse_task_states_data = RayTaskStateSerializer(parse_task_states, many=True).data

        ray_task_states = ray_api.list_tasks()
        tasks = []
        for task in ray_task_states:
            tasks.append(ray_api.get_task(task.task_id))
        ray_task_states_data = []
        for task in tasks:
            ray_task_states_data.append(task.__dict__)

        return parse_task_states_data + ray_task_states_data
