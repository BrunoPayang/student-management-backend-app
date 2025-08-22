from rest_framework import serializers
from django_celery_results.models import TaskResult


class TaskResultSerializer(serializers.ModelSerializer):
    """Serializer for TaskResult model"""
    
    class Meta:
        model = TaskResult
        fields = [
            'id', 'task_id', 'periodic_task_name', 'task_name', 'task_args', 
            'task_kwargs', 'status', 'worker', 'content_type', 'content_encoding', 
            'result', 'date_created', 'date_started', 'date_done', 'traceback', 'meta'
        ]
        read_only_fields = fields  # All fields are read-only for task results

