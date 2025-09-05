from rest_framework import serializers
from django.core.validators import RegexValidator
from .models import Class, Student, ParentStudent, Transcript, BehaviorReport, PaymentRecord


class ClassListSerializer(serializers.ModelSerializer):
    """Serializer for class list view"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    student_count = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    
    class Meta:
        model = Class
        fields = [
            'id', 'name', 'level', 'section', 'full_name',
            'school', 'school_name', 'academic_year', 'max_students',
            'student_count', 'available_spots', 'is_active',
            'created_at', 'updated_at'
        ]


class ClassDetailSerializer(serializers.ModelSerializer):
    """Serializer for class detail view"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    student_count = serializers.ReadOnlyField()
    available_spots = serializers.ReadOnlyField()
    students = serializers.SerializerMethodField()
    
    class Meta:
        model = Class
        fields = [
            'id', 'name', 'level', 'section', 'full_name', 'description',
            'school', 'school_name', 'academic_year', 'max_students',
            'student_count', 'available_spots', 'is_active',
            'students', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_students(self, obj):
        """Get list of students in this class"""
        students = obj.students.filter(is_active=True)
        return [{
            'id': student.id,
            'name': student.full_name,
            'student_id': student.student_id,
            'enrollment_date': student.enrollment_date
        } for student in students]


class ClassCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating classes"""
    
    class Meta:
        model = Class
        fields = [
            'name', 'level', 'section', 'description',
            'academic_year', 'max_students', 'is_active'
        ]
    
    def validate(self, data):
        """Validate class data"""
        school = self.context['request'].user.school
        if not school:
            raise serializers.ValidationError("L'utilisateur doit être associé à une école.")
        
        # Check for duplicate class name within the same school and academic year
        name = data.get('name')
        section = data.get('section')
        academic_year = data.get('academic_year')
        
        if Class.objects.filter(
            school=school,
            name=name,
            section=section,
            academic_year=academic_year
        ).exists():
            raise serializers.ValidationError(
                f"Une classe avec le nom '{name}' et la section '{section}' existe déjà pour l'année académique {academic_year}."
            )
        
        return data
    
    def create(self, validated_data):
        """Create class and assign to user's school"""
        school = self.context['request'].user.school
        validated_data['school'] = school
        return super().create(validated_data)


class ClassUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating classes"""
    
    class Meta:
        model = Class
        fields = [
            'name', 'level', 'section', 'description',
            'academic_year', 'max_students', 'is_active'
        ]
    
    def validate(self, data):
        """Validate class update data"""
        school = self.context['request'].user.school
        if not school:
            raise serializers.ValidationError("L'utilisateur doit être associé à une école.")
        
        # Check for duplicate class name within the same school and academic year
        # (excluding current instance)
        name = data.get('name')
        section = data.get('section')
        academic_year = data.get('academic_year')
        
        if name and section and academic_year:
            existing_classes = Class.objects.filter(
                school=school,
                name=name,
                section=section,
                academic_year=academic_year
            ).exclude(id=self.instance.id)
            
            if existing_classes.exists():
                raise serializers.ValidationError(
                    f"Une classe avec le nom '{name}' et la section '{section}' existe déjà pour l'année académique {academic_year}."
                )
        
        return data


class StudentListSerializer(serializers.ModelSerializer):
    """Serializer for student list view"""
    school_name = serializers.CharField(source='school.name', read_only=True)
    class_name = serializers.CharField(source='class_assigned.full_name', read_only=True)
    primary_parent = serializers.SerializerMethodField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'student_id',
            'school', 'school_name', 'class_assigned', 'class_name',
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
    class_name = serializers.CharField(source='class_assigned.full_name', read_only=True)
    parents = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'middle_name', 'student_id',
            'school', 'school_name', 'class_assigned', 'class_name',
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
            'class_assigned', 'date_of_birth', 'gender',
            'email', 'phone', 'address', 'city', 'state',
            'blood_group', 'emergency_contact', 'medical_conditions',
            'profile_picture'
        ]
    
    def validate_student_id(self, value):
        """Ensure student ID is unique within school"""
        school = self.initial_data.get('school')
        if school and Student.objects.filter(school=school, student_id=value).exists():
            raise serializers.ValidationError("Un étudiant avec cet ID existe déjà dans cette école.")
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
            'class_assigned', 'date_of_birth', 'gender',
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