from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from rest_framework import serializers

from .models import FileUpload
from .serializers import FileUploadSerializer, FileUploadCreateSerializer
from .services import FirebaseStorageService
from apps.authentication.permissions import IsSchoolStaff, IsParent, IsSchoolStaffOrSystemAdmin
from apps.common.pagination import StandardResultsSetPagination

@extend_schema_view(
    list=extend_schema(
        summary="List Files",
        description="Retrieve a list of files with pagination and filtering",
        tags=['files'],
        parameters=[
            OpenApiParameter(name='file_type', description='Filter by file type', required=False),
            OpenApiParameter(name='is_public', description='Filter by public status', required=False),
            OpenApiParameter(name='uploaded_by', description='Filter by uploader', required=False),
        ]
    ),
    create=extend_schema(
        summary="Create File Upload",
        description="Upload a new file with metadata. This endpoint handles both file upload and metadata creation.",
        tags=['files'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {'type': 'string', 'format': 'binary', 'description': 'File to upload'},
                    'file_type': {'type': 'string', 'enum': ['transcript', 'behavior_report', 'payment_receipt', 'student_document', 'other']},
                    'description': {'type': 'string', 'description': 'File description (optional)'},
                    'tags': {'type': 'string', 'description': 'Comma-separated tags (optional)'},
                    'is_public': {'type': 'boolean', 'description': 'Whether file is public (default: false)'}
                },
                'required': ['file', 'file_type']
            }
        },
        responses={
            201: FileUploadSerializer,
            400: {'description': 'Validation error'},
            500: {'description': 'Upload failed'}
        }
    ),
    retrieve=extend_schema(
        summary="Get File Details",
        description="Retrieve detailed information about a specific file",
        tags=['files']
    ),
    update=extend_schema(
        summary="Update File",
        description="Update file metadata (not the actual file content)",
        tags=['files']
    ),
    destroy=extend_schema(
        summary="Delete File",
        description="Mark file as deleted (soft delete)",
        tags=['files']
    )
)
class FileUploadViewSet(viewsets.ModelViewSet):
    """ViewSet for file upload management with local storage and Firebase support"""
    queryset = FileUpload.objects.all()
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['file_type', 'is_public', 'uploaded_by']
    search_fields = ['original_name', 'description', 'tags']

    def get_queryset(self):
        """Filter by school and permissions"""
        user = self.request.user

        if user.is_system_admin():
            return FileUpload.objects.filter(is_deleted=False)
        elif user.is_school_staff():
            return FileUpload.objects.filter(
                school=user.school,
                is_deleted=False
            )
        elif user.is_parent():
            # Parents can see files related to their children
            return FileUpload.objects.filter(
                school__students__parents__parent=user,
                is_public=True,
                is_deleted=False
            ).distinct()
        else:
            return FileUpload.objects.none()

    def get_serializer_class(self):
        """Return appropriate serializer"""
        if self.action == 'create':
            return FileUploadCreateSerializer
        return FileUploadSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsSchoolStaffOrSystemAdmin]  # Only staff and admins can manage files
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Create file upload with file processing"""
        # Check if user has a school
        if not hasattr(self.request.user, 'school') or not self.request.user.school:
            raise serializers.ValidationError("User must be associated with a school to upload files")
        
        file_obj = serializer.validated_data.pop('file')
        
        # Get upload data
        file_type = serializer.validated_data.get('file_type', 'other')
        description = serializer.validated_data.get('description', '')
        tags = serializer.validated_data.get('tags', '')
        is_public = serializer.validated_data.get('is_public', False)

        # Upload to storage
        firebase_service = FirebaseStorageService()
        folder = f"schools/{self.request.user.school.id}/{file_type}"

        upload_result = firebase_service.upload_file(file_obj, folder)

        # Create database record
        file_upload = FileUpload.objects.create(
            school=self.request.user.school,
            original_name=file_obj.name,
            firebase_path=upload_result['path'],
            firebase_url=upload_result['url'],
            file_size=upload_result['size'],
            content_type=upload_result['content_type'],
            file_type=file_type,
            description=description,
            tags=tags,
            is_public=is_public,
            uploaded_by=self.request.user
        )
        
        # Update the serializer instance to use the full serializer for response
        serializer.instance = file_upload
        # Use the full serializer for the response
        response_serializer = FileUploadSerializer(file_upload)
        serializer._data = response_serializer.data

    @extend_schema(
        summary="Upload File",
        description="""
        Upload a file to storage (local or Firebase).
        
        **Features:**
        - Supports multiple file types (PDF, DOC, JPG, PNG, etc.)
        - Automatic file validation (size, type)
        - School-based folder organization
        - Automatic storage selection (local/Firebase)
        
        **Storage Behavior:**
        - If Firebase is configured: Uses Firebase Storage
        - If Firebase not configured: Uses local storage (free)
        
        **File Types Allowed:**
        - Documents: PDF, DOC, DOCX
        - Images: JPG, JPEG, PNG, GIF
        - Text: TXT
        
        **Tags (Optional):**
        - Can be left empty
        - Use comma-separated values (e.g., "academic, transcript, 2024")
        - Not required for file upload
        """,
        tags=['files'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {'type': 'string', 'format': 'binary'},
                    'file_type': {'type': 'string', 'enum': ['transcript', 'behavior_report', 'payment_receipt', 'student_document', 'other']},
                    'description': {'type': 'string'},
                    'tags': {'type': 'string', 'description': 'Comma-separated tags (optional)'},
                    'is_public': {'type': 'boolean'}
                },
                'required': ['file', 'file_type']
            }
        },
        responses={
            201: FileUploadSerializer,
            400: {'description': 'Validation error'},
            500: {'description': 'Upload failed'}
        },
        examples=[
            OpenApiExample(
                'Upload Transcript',
                value={
                    'file_type': 'transcript',
                    'description': 'Student academic transcript for 2024',
                    'tags': 'academic, transcript, 2024',
                    'is_public': False
                },
                request_only=True
            ),
            OpenApiExample(
                'Upload Behavior Report',
                value={
                    'file_type': 'behavior_report',
                    'description': 'Monthly behavior assessment',
                    'tags': 'behavior, monthly',
                    'is_public': True
                },
                request_only=True
            ),
            OpenApiExample(
                'Upload Without Tags',
                value={
                    'file_type': 'student_document',
                    'description': 'Student ID card',
                    'is_public': True
                },
                request_only=True
            )
        ]
    )
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload file to storage (Firebase or local)"""
        try:
            file_obj = request.FILES.get('file')
            if not file_obj:
                return Response(
                    {'error': 'No file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get upload data
            file_type = request.data.get('file_type', 'other')
            description = request.data.get('description', '')
            tags = request.data.get('tags', '')  # Tags is now a string
            is_public = request.data.get('is_public', False)

            # Upload to storage
            firebase_service = FirebaseStorageService()
            folder = f"schools/{request.user.school.id}/{file_type}"

            upload_result = firebase_service.upload_file(file_obj, folder)

            # Create database record
            file_upload = FileUpload.objects.create(
                school=request.user.school,
                original_name=file_obj.name,
                firebase_path=upload_result['path'],
                firebase_url=upload_result['url'],
                file_size=upload_result['size'],
                content_type=upload_result['content_type'],
                file_type=file_type,
                description=description,
                tags=tags,  # Store tags as string
                is_public=is_public,
                uploaded_by=request.user
            )

            serializer = FileUploadSerializer(file_upload)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'File upload failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Delete File",
        description="Delete file from storage and mark as deleted in database",
        tags=['files'],
        responses={
            200: {'description': 'File deleted successfully'},
            500: {'description': 'Deletion failed'}
        }
    )
    @action(detail=True, methods=['post'])
    def delete_file(self, request, pk=None):
        """Delete file from storage and database"""
        file_upload = self.get_object()

        try:
            # Delete from storage
            firebase_service = FirebaseStorageService()
            firebase_service.delete_file(file_upload.firebase_path)

            # Mark as deleted in database
            file_upload.is_deleted = True
            file_upload.save()

            return Response({'message': 'File deleted successfully'})

        except Exception as e:
            return Response(
                {'error': 'File deletion failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Search Files",
        description="Search files by name, description, or tags",
        tags=['files'],
        parameters=[
            OpenApiParameter(name='q', description='Search query', required=True, type=str)
        ],
        responses={
            200: FileUploadSerializer(many=True),
            400: {'description': 'Search query required'}
        }
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search files by name, description, or tags"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query required'})

        files = self.get_queryset().filter(
            Q(original_name__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)  # Search in tags text field
        )

        serializer = self.get_serializer(files, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Test File Upload",
        description="Simple endpoint to test file upload functionality. Upload a file with basic metadata.",
        tags=['files'],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {'type': 'string', 'format': 'binary', 'description': 'File to upload (PDF, DOC, JPG, PNG, TXT)'},
                    'file_type': {'type': 'string', 'enum': ['transcript', 'behavior_report', 'payment_receipt', 'student_document', 'other']},
                    'description': {'type': 'string', 'description': 'File description (optional)'},
                    'tags': {'type': 'string', 'description': 'Comma-separated tags like: academic, important, 2024 (optional)'},
                    'is_public': {'type': 'boolean', 'description': 'Whether file is public (default: false)'}
                },
                'required': ['file', 'file_type']
            }
        },
        responses={
            201: FileUploadSerializer,
            400: {'description': 'Validation error'},
            500: {'description': 'Upload failed'}
        },
        examples=[
            OpenApiExample(
                'Upload Transcript',
                value={
                    'file_type': 'transcript',
                    'description': 'Student academic transcript for 2024',
                    'tags': 'academic, transcript, 2024',
                    'is_public': False
                },
                request_only=True
            ),
            OpenApiExample(
                'Upload Document',
                value={
                    'file_type': 'student_document',
                    'description': 'Student ID card',
                    'tags': 'identification, student',
                    'is_public': True
                },
                request_only=True
            )
        ]
    )
    @action(detail=False, methods=['post'])
    def test_upload(self, request):
        """Simple test endpoint for file uploads"""
        return self.create(request)
