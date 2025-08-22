from rest_framework import serializers
from django_celery_results.models import TaskResult


class TaskResultSerializer(serializers.ModelSerializer):
    """Serializer for TaskResult model"""
    
    class Meta:
        model = TaskResult
        fields = [
            'task_id', 'task_name', 'task_args', 'task_kwargs', 
            'status', 'content_type', 'content_encoding', 'result',
            'date_done', 'traceback', 'hidden', 'meta'
        ]
        read_only_fields = fields  # All fields are read-only for task results

