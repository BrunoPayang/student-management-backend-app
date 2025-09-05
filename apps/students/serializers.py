from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import Student, ParentStudent, Transcript, BehaviorReport, PaymentRecord


class StudentListSerializer(serializers.ModelSerializer):
    """Serializer for student list view"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    primary_parent = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'student_id',
            'school', 'school_name', 'class_level', 'section',
            'gender', 'is_active', 'enrollment_date', 'primary_parent'
        ]
    
    def get_primary_parent(self, obj):
        primary_parent = obj.get_primary_parent()
        if primary_parent:
            return {
                'id': primary_parent.parent.id,
                'name': primary_parent.parent.full_name,
                'phone': primary_parent.parent.phone
            }
        return None


class StudentDetailSerializer(serializers.ModelSerializer):
    """Serializer for student detail view"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    parents = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'student_id',
            'school', 'school_name', 'class_level', 'section',
            'date_of_birth', 'age', 'gender', 'email', 'phone',
            'address', 'city', 'state', 'blood_group', 'emergency_contact',
            'medical_conditions', 'enrollment_date', 'graduation_date',
            'is_active', 'is_graduated', 'profile_picture', 'parents',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_parents(self, obj):
        parents = obj.parents.all()
        return [{
            'id': parent.parent.id,
            'name': parent.parent.full_name,
            'relationship': parent.relationship,
            'is_primary': parent.is_primary,
            'is_emergency_contact': parent.is_emergency_contact,
            'phone': parent.parent.phone,
            'email': parent.parent.email
        } for parent in parents]


class StudentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating students"""
    
    class Meta:
        model = Student
        fields = [
            'school', 'first_name', 'last_name', 'middle_name', 'student_id',
            'class_level', 'section', 'date_of_birth', 'gender',
            'email', 'phone', 'address', 'city', 'state',
            'blood_group', 'emergency_contact', 'medical_conditions',
            'profile_picture'
        ]
    
    def validate_student_id(self, value):
        """Ensure student ID is unique within school"""
        school = self.initial_data.get('school')
        if school and Student.objects.filter(school=school, student_id=value).exists():
            raise serializers.ValidationError("A student with this ID already exists in this school.")
        return value
    
    def create(self, validated_data):
        """Create student"""
        return super().create(validated_data)


class StudentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating students"""
    
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'middle_name', 'student_id',
            'class_level', 'section', 'date_of_birth', 'gender',
            'email', 'phone', 'address', 'city', 'state',
            'blood_group', 'emergency_contact', 'medical_conditions',
            'enrollment_date', 'graduation_date', 'is_active',
            'is_graduated', 'profile_picture'
        ]


class ParentStudentSerializer(serializers.ModelSerializer):
    """Serializer for parent-student relationships"""
    parent_name = serializers.CharField(source='parent.full_name', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    
    class Meta:
        model = ParentStudent
        fields = [
            'id', 'parent', 'parent_name', 'student', 'student_name',
            'relationship', 'is_primary', 'is_emergency_contact',
            'receive_sms', 'receive_email', 'receive_push',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class TranscriptSerializer(serializers.ModelSerializer):
    """Serializer for academic transcripts"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)
    
    class Meta:
        model = Transcript
        fields = [
            'id', 'student', 'student_name', 'academic_year', 'semester',
            'file_url', 'file_name', 'gpa', 'total_credits',
            'rank_in_class', 'class_size', 'uploaded_by', 'uploaded_by_name',
            'is_public', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BehaviorReportSerializer(serializers.ModelSerializer):
    """Serializer for behavior reports"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    reported_by_name = serializers.CharField(source='reported_by.full_name', read_only=True)
    
    class Meta:
        model = BehaviorReport
        fields = [
            'id', 'student', 'student_name', 'report_type', 'title',
            'description', 'location', 'incident_date', 'incident_time',
            'severity_level', 'actions_taken', 'follow_up_required',
            'follow_up_date', 'reported_by', 'reported_by_name',
            'notify_parents', 'is_public', 'created_at'
        ]
        read_only_fields = ['id', 'reported_by', 'created_at']


class PaymentRecordSerializer(serializers.ModelSerializer):
    """Serializer for payment records"""
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    days_overdue = serializers.ReadOnlyField()
    
    class Meta:
        model = PaymentRecord
        fields = [
            'id', 'student', 'student_name', 'amount', 'currency',
            'payment_type', 'status', 'due_date', 'paid_date',
            'payment_method', 'reference_number', 'receipt_url',
            'notes', 'created_by', 'created_by_name', 'days_overdue',
            'created_at'
        ]
        read_only_fields = ['id', 'days_overdue', 'created_at'] 