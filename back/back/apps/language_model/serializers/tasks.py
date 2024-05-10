from rest_framework import serializers

from back.apps.language_model.models import RayTaskState


class RayTaskStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RayTaskState
        fields = '__all__'
        read_only_fields = ('task_id', 'state', 'type', 'func_or_class_name', 'creation_time_ms', 'start_time_ms',
                            'end_time_ms', 'task_log_info', 'error_message', 'is_debugger_paused')
