from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from datetime import date
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from .models import Class, Student, ParentStudent, Transcript, BehaviorReport, PaymentRecord
from .serializers import (
    ClassListSerializer, ClassDetailSerializer, ClassCreateSerializer, ClassUpdateSerializer,
    StudentListSerializer, StudentDetailSerializer,
    StudentCreateSerializer, StudentUpdateSerializer,
    ParentStudentSerializer, TranscriptSerializer,
    BehaviorReportSerializer, PaymentRecordSerializer
)
from apps.common.pagination import StandardResultsSetPagination


@extend_schema_view(
    list=extend_schema(
        summary="Liste des Classes",
        description="Récupère la liste paginée des classes de l'école avec options de filtrage et de recherche.",
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Rechercher par nom de classe, section ou description'
            ),
            OpenApiParameter(
                name='academic_year',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrer par année académique (ex: '2024-2025')"
            ),
            OpenApiParameter(
                name='level',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrer par niveau de classe (ex: '1', '2', '3')"
            ),
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filtrer par statut actif'
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Trier par: name, level, created_at, student_count'
            )
        ],
        examples=[
            OpenApiExample(
                'Liste des classes',
                summary='Exemple de réponse',
                description='Liste paginée des classes avec informations de base',
                value={
                    "count": 12,
                    "next": "http://localhost:8000/api/classes/?page=2",
                    "previous": None,
                    "results": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Grade 1",
                            "level": "1",
                            "section": "A",
                            "full_name": "Grade 1 - A",
                            "school": "123e4567-e89b-12d3-a456-426614174001",
                            "school_name": "École Primaire de Niamey",
                            "academic_year": "2024-2025",
                            "max_students": 30,
                            "student_count": 25,
                            "available_spots": 5,
                            "is_active": True,
                            "created_at": "2024-01-15T10:30:00Z",
                            "updated_at": "2024-09-04T14:20:00Z"
                        }
                    ]
                }
            )
        ]
    ),
    create=extend_schema(
        summary="Créer une Classe",
        description="Crée une nouvelle classe pour l'école de l'utilisateur connecté.",
        request=ClassCreateSerializer,
        examples=[
            OpenApiExample(
                'Création de classe',
                summary='Exemple de création',
                description='Créer une nouvelle classe avec toutes les informations',
                value={
                    "name": "Grade 2",
                    "level": "2",
                    "section": "B",
                    "description": "Classe de deuxième année avec section B",
                    "academic_year": "2024-2025",
                    "max_students": 25,
                    "is_active": True
                }
            ),
            OpenApiExample(
                'Création simple',
                summary='Création minimale',
                description='Créer une classe avec seulement les champs requis',
                value={
                    "name": "Grade 3",
                    "level": "3",
                    "academic_year": "2024-2025"
                }
            )
        ]
    ),
    retrieve=extend_schema(
        summary="Détails d'une Classe",
        description="Récupère les détails complets d'une classe spécifique, y compris la liste des étudiants.",
        examples=[
            OpenApiExample(
                'Détails de classe',
                summary='Exemple de réponse',
                description='Détails complets d\'une classe avec liste des étudiants',
                value={
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "Grade 1",
                    "level": "1",
                    "section": "A",
                    "full_name": "Grade 1 - A",
                    "description": "Classe de première année section A",
                    "school": "123e4567-e89b-12d3-a456-426614174001",
                    "school_name": "École Primaire de Niamey",
                    "academic_year": "2024-2025",
                    "max_students": 30,
                    "student_count": 25,
                    "available_spots": 5,
                    "is_active": True,
                    "students": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174002",
                            "name": "Aminata Traoré",
                            "student_id": "STU001",
                            "enrollment_date": "2024-09-01"
                        }
                    ],
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-09-04T14:20:00Z"
                }
            )
        ]
    ),
    update=extend_schema(
        summary="Mettre à jour une Classe (Complet)",
        description="Met à jour toutes les informations d'une classe (mise à jour complète).",
        request=ClassUpdateSerializer,
        examples=[
            OpenApiExample(
                'Mise à jour complète',
                summary='Exemple de mise à jour',
                description='Mettre à jour toutes les informations de la classe',
                value={
                    "name": "Grade 2 - Mise à jour",
                    "level": "2",
                    "section": "C",
                    "description": "Classe de deuxième année section C - Mise à jour",
                    "academic_year": "2024-2025",
                    "max_students": 35,
                    "is_active": True
                }
            )
        ]
    ),
    partial_update=extend_schema(
        summary="Mettre à jour une Classe (Partiel)",
        description="Met à jour partiellement les informations d'une classe.",
        request=ClassUpdateSerializer,
        examples=[
            OpenApiExample(
                'Mise à jour partielle - Nom',
                summary='Changer le nom',
                description='Mettre à jour seulement le nom de la classe',
                value={
                    "name": "Grade 2 - Nouveau Nom"
                }
            ),
            OpenApiExample(
                'Mise à jour partielle - Capacité',
                summary='Changer la capacité',
                description='Mettre à jour seulement la capacité maximale',
                value={
                    "max_students": 40
                }
            ),
            OpenApiExample(
                'Mise à jour partielle - Statut',
                summary='Désactiver la classe',
                description='Désactiver la classe',
                value={
                    "is_active": False
                }
            )
        ]
    ),
    destroy=extend_schema(
        summary="Supprimer une Classe",
        description="Supprime définitivement une classe de l'école.",
        examples=[
            OpenApiExample(
                'Suppression réussie',
                summary='Réponse de suppression',
                description='Confirmation de suppression de la classe',
                value={
                    "message": "Classe supprimée avec succès"
                }
            )
        ]
    )
)
class ClassViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des classes d'école
    Seul le personnel de l'école peut gérer les classes de leur propre école
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['academic_year', 'is_active', 'level']
    search_fields = ['name', 'section', 'description']
    ordering_fields = ['name', 'level', 'created_at', 'student_count']
    ordering = ['level', 'name', 'section']
    
    def get_queryset(self):
        """Filter classes by user's school"""
        user = self.request.user
        if user.is_superuser:
            return Class.objects.all()
        elif user.user_type == 'school_staff' and user.school:
            return Class.objects.filter(school=user.school)
        else:
            return Class.objects.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ClassListSerializer
        elif self.action == 'create':
            return ClassCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ClassUpdateSerializer
        return ClassDetailSerializer
    
    def perform_create(self, serializer):
        """Create class and assign to user's school"""
        school = self.request.user.school
        if not school:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("L'utilisateur doit être associé à une école.")
        serializer.save(school=school)
    
    def check_permissions(self, request):
        """Check permissions for class operations"""
        super().check_permissions(request)
        if not request.user.is_superuser and request.user.user_type != 'school_staff':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Seul le personnel de l'école peut gérer les classes.")
    
    @extend_schema(
        summary="Liste des Étudiants de la Classe",
        description="Récupère la liste paginée de tous les étudiants actifs dans cette classe.",
        parameters=[
            OpenApiParameter(
                name='page',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Numéro de page pour la pagination'
            ),
            OpenApiParameter(
                name='page_size',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Nombre d\'éléments par page'
            )
        ],
        examples=[
            OpenApiExample(
                'Liste des étudiants',
                summary='Exemple de réponse',
                description='Liste paginée des étudiants de la classe',
                value={
                    "count": 25,
                    "next": "http://localhost:8000/api/classes/123/students/?page=2",
                    "previous": None,
                    "results": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174002",
                            "first_name": "Aminata",
                            "last_name": "Traoré",
                            "student_id": "STU001",
                            "school": "123e4567-e89b-12d3-a456-426614174001",
                            "school_name": "École Primaire de Niamey",
                            "class_assigned": "123e4567-e89b-12d3-a456-426614174000",
                            "class_name": "Grade 1 - A",
                            "gender": "Féminin",
                            "is_active": True,
                            "enrollment_date": "2024-09-01",
                            "primary_parent": {
                                "id": "123e4567-e89b-12d3-a456-426614174003",
                                "name": "Mariam Traoré",
                                "phone": "+22712345678"
                            }
                        }
                    ]
                }
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """Récupère tous les étudiants de cette classe"""
        class_obj = self.get_object()
        students = class_obj.students.filter(is_active=True)
        
        # Apply pagination
        page = self.paginate_queryset(students)
        if page is not None:
            serializer = StudentListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = StudentListSerializer(students, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Ajouter un Étudiant à la Classe",
        description="Ajoute un étudiant existant à cette classe. L'étudiant doit être dans la même école et la classe doit avoir des places disponibles.",
        request={
            'type': 'object',
            'properties': {
                'student_id': {
                    'type': 'string',
                    'description': 'ID de l\'étudiant à ajouter à la classe',
                    'example': '123e4567-e89b-12d3-a456-426614174002'
                }
            },
            'required': ['student_id']
        },
        examples=[
            OpenApiExample(
                'Ajouter un étudiant',
                summary='Exemple de requête',
                description='Ajouter un étudiant à la classe',
                value={
                    "student_id": "123e4567-e89b-12d3-a456-426614174002"
                }
            )
        ],
        responses={
            200: OpenApiExample(
                'Succès',
                summary='Étudiant ajouté avec succès',
                description='L\'étudiant a été ajouté à la classe',
                value={
                    "id": "123e4567-e89b-12d3-a456-426614174002",
                    "first_name": "Aminata",
                    "last_name": "Traoré",
                    "student_id": "STU001",
                    "class_assigned": "123e4567-e89b-12d3-a456-426614174000",
                    "class_name": "Grade 1 - A",
                    "gender": "Féminin",
                    "is_active": True,
                    "enrollment_date": "2024-09-01"
                }
            ),
            400: OpenApiExample(
                'Erreur - Champs requis',
                summary='student_id manquant',
                description='Le champ student_id est requis',
                value={
                    "error": "student_id est requis"
                }
            ),
            400: OpenApiExample(
                'Erreur - Classe pleine',
                summary='Aucune place disponible',
                description='La classe est pleine',
                value={
                    "error": "La classe est pleine. Aucune place disponible."
                }
            ),
            404: OpenApiExample(
                'Erreur - Étudiant non trouvé',
                summary='Étudiant introuvable',
                description='L\'étudiant n\'existe pas ou n\'est pas dans la même école',
                value={
                    "error": "Étudiant non trouvé ou pas dans la même école"
                }
            )
        }
    )
    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """Ajoute un étudiant à cette classe"""
        class_obj = self.get_object()
        student_id = request.data.get('student_id')
        
        if not student_id:
            return Response(
                {'error': 'student_id est requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            student = Student.objects.get(
                id=student_id, 
                school=class_obj.school,
                is_active=True
            )
            
            # Check if class has available spots
            if class_obj.available_spots <= 0:
                return Response(
                    {'error': 'La classe est pleine. Aucune place disponible.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            student.class_assigned = class_obj
            student.save()
            
            serializer = StudentDetailSerializer(student)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Student.DoesNotExist:
            return Response(
                {'error': 'Étudiant non trouvé ou pas dans la même école'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Retirer un Étudiant de la Classe",
        description="Retire un étudiant de cette classe. L'étudiant doit être actuellement dans cette classe.",
        request={
            'type': 'object',
            'properties': {
                'student_id': {
                    'type': 'string',
                    'description': 'ID de l\'étudiant à retirer de la classe',
                    'example': '123e4567-e89b-12d3-a456-426614174002'
                }
            },
            'required': ['student_id']
        },
        examples=[
            OpenApiExample(
                'Retirer un étudiant',
                summary='Exemple de requête',
                description='Retirer un étudiant de la classe',
                value={
                    "student_id": "123e4567-e89b-12d3-a456-426614174002"
                }
            )
        ],
        responses={
            200: OpenApiExample(
                'Succès',
                summary='Étudiant retiré avec succès',
                description='L\'étudiant a été retiré de la classe',
                value={
                    "message": "Étudiant retiré de la classe avec succès"
                }
            ),
            400: OpenApiExample(
                'Erreur - Champs requis',
                summary='student_id manquant',
                description='Le champ student_id est requis',
                value={
                    "error": "student_id est requis"
                }
            ),
            404: OpenApiExample(
                'Erreur - Étudiant non trouvé',
                summary='Étudiant introuvable',
                description='L\'étudiant n\'est pas dans cette classe',
                value={
                    "error": "Étudiant non trouvé dans cette classe"
                }
            )
        }
    )
    @action(detail=True, methods=['post'])
    def remove_student(self, request, pk=None):
        """Retire un étudiant de cette classe"""
        class_obj = self.get_object()
        student_id = request.data.get('student_id')
        
        if not student_id:
            return Response(
                {'error': 'student_id est requis'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            student = Student.objects.get(
                id=student_id, 
                class_assigned=class_obj,
                is_active=True
            )
            
            student.class_assigned = None
            student.save()
            
            return Response(
                {'message': 'Étudiant retiré de la classe avec succès'}, 
                status=status.HTTP_200_OK
            )
            
        except Student.DoesNotExist:
            return Response(
                {'error': 'Étudiant non trouvé dans cette classe'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @extend_schema(
        summary="Statistiques des Classes",
        description="Récupère les statistiques complètes des classes de l'école, incluant la distribution par niveau et les classes les plus peuplées.",
        examples=[
            OpenApiExample(
                'Statistiques des classes',
                summary='Exemple de réponse',
                description='Statistiques complètes des classes de l\'école',
                value={
                    "total_classes": 12,
                    "active_classes": 10,
                    "total_students": 285,
                    "level_distribution": [
                        {
                            "level": "1",
                            "count": 2,
                            "total_students": 45
                        },
                        {
                            "level": "2",
                            "count": 2,
                            "total_students": 50
                        },
                        {
                            "level": "3",
                            "count": 2,
                            "total_students": 48
                        }
                    ],
                    "most_populated_classes": [
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "name": "Grade 1 - A",
                            "student_count": 30,
                            "max_students": 30,
                            "available_spots": 0
                        },
                        {
                            "id": "123e4567-e89b-12d3-a456-426614174001",
                            "name": "Grade 2 - B",
                            "student_count": 28,
                            "max_students": 30,
                            "available_spots": 2
                        }
                    ]
                }
            )
        ]
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Récupère les statistiques des classes de l'école"""
        classes = self.get_queryset()
        
        total_classes = classes.count()
        active_classes = classes.filter(is_active=True).count()
        total_students = sum(class_obj.student_count for class_obj in classes)
        
        # Class distribution by level
        level_distribution = classes.values('level').annotate(
            count=Count('id'),
            total_students=Sum('students__id', filter=Q(students__is_active=True))
        ).order_by('level')
        
        # Most populated classes
        most_populated = classes.filter(is_active=True).annotate(
            student_count=Count('students', filter=Q(students__is_active=True))
        ).order_by('-student_count')[:5]
        
        most_populated_data = [{
            'id': str(class_obj.id),
            'name': class_obj.full_name,
            'student_count': class_obj.student_count,
            'max_students': class_obj.max_students,
            'available_spots': class_obj.available_spots
        } for class_obj in most_populated]
        
        return Response({
            'total_classes': total_classes,
            'active_classes': active_classes,
            'total_students': total_students,
            'level_distribution': list(level_distribution),
            'most_populated_classes': most_populated_data
        })


class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for student management
    School staff can manage students in their school
    Parents can view their children
    """
    queryset = Student.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_assigned', 'gender', 'is_active', 'is_graduated']
    search_fields = ['first_name', 'last_name', 'student_id', 'email']
    ordering_fields = ['first_name', 'last_name', 'enrollment_date', 'date_of_birth']
    ordering = ['last_name', 'first_name']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        user = self.request.user
        
        if user.user_type == 'admin':
            # System Admin can see all students
            return Student.objects.all()
        elif user.user_type == 'school_staff' and user.school:
            # School Staff can only see students from their school
            return Student.objects.filter(school=user.school)
        elif user.user_type == 'parent':
            # Parents can only see their own children
            return Student.objects.filter(parents__parent=user)
        else:
            # For other cases, return empty queryset
            return Student.objects.none()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return StudentListSerializer
        elif self.action == 'create':
            return StudentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return StudentUpdateSerializer
        else:
            return StudentDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Create student with school context"""
        # Use school from request data if provided, otherwise use user's school
        school = serializer.validated_data.get('school')
        if not school and hasattr(self.request.user, 'school') and self.request.user.school:
            school = self.request.user.school
            serializer.save(school=school)
        else:
            serializer.save()
    
    @action(detail=True, methods=['get'])
    def academic_records(self, request, pk=None):
        """Get student's academic records"""
        student = self.get_object()
        transcripts = student.transcripts.filter(is_public=True)
        serializer = TranscriptSerializer(transcripts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def behavior_reports(self, request, pk=None):
        """Get student's behavior reports"""
        student = self.get_object()
        reports = student.behavior_reports.filter(is_public=True)
        serializer = BehaviorReportSerializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payment_records(self, request, pk=None):
        """Get student's payment records"""
        student = self.get_object()
        payments = student.payment_records.all()
        serializer = PaymentRecordSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get student statistics"""
        student = self.get_object()
        
        # Academic statistics
        transcripts = student.transcripts.all()
        total_transcripts = transcripts.count()
        average_gpa = transcripts.aggregate(avg_gpa=Avg('gpa'))['avg_gpa']
        
        # Behavior statistics
        behavior_reports = student.behavior_reports.all()
        positive_reports = behavior_reports.filter(report_type='positive').count()
        negative_reports = behavior_reports.filter(report_type='negative').count()
        
        # Payment statistics
        payments = student.payment_records.all()
        total_payments = payments.count()
        paid_payments = payments.filter(status='paid').count()
        overdue_payments = payments.filter(status='overdue').count()
        total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'academic': {
                'total_transcripts': total_transcripts,
                'average_gpa': average_gpa
            },
            'behavior': {
                'positive_reports': positive_reports,
                'negative_reports': negative_reports,
                'total_reports': behavior_reports.count()
            },
            'payments': {
                'total_payments': total_payments,
                'paid_payments': paid_payments,
                'overdue_payments': overdue_payments,
                'total_amount': total_amount
            }
        })


class ParentStudentViewSet(viewsets.ModelViewSet):
    """ViewSet for parent-student relationships"""
    queryset = ParentStudent.objects.all()
    serializer_class = ParentStudentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter by school"""
        return ParentStudent.objects.filter(student__school=self.request.user.school)
    
    def perform_create(self, serializer):
        """Create relationship with validation"""
        # Ensure only one primary contact per student
        if serializer.validated_data.get('is_primary'):
            ParentStudent.objects.filter(
                student=serializer.validated_data['student'],
                is_primary=True
            ).update(is_primary=False)
        
        serializer.save()


class TranscriptViewSet(viewsets.ModelViewSet):
    """ViewSet for academic transcripts"""
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['academic_year', 'semester', 'is_public']
    search_fields = ['student__first_name', 'student__last_name', 'student__student_id']
    
    def get_queryset(self):
        """Filter by school"""
        return Transcript.objects.filter(student__school=self.request.user.school)
    
    def perform_create(self, serializer):
        """Create transcript with uploader info"""
        serializer.save(uploaded_by=self.request.user)


class BehaviorReportViewSet(viewsets.ModelViewSet):
    """ViewSet for behavior reports"""
    queryset = BehaviorReport.objects.all()
    serializer_class = BehaviorReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['report_type', 'severity_level', 'notify_parents', 'is_public']
    search_fields = ['student__first_name', 'student__last_name', 'title', 'description']
    
    def get_queryset(self):
        """Filter by school"""
        return BehaviorReport.objects.filter(student__school=self.request.user.school)
    
    def perform_create(self, serializer):
        """Create report with reporter info"""
        report = serializer.save(reported_by=self.request.user)
        
        # Send notification to parents if enabled
        if report.notify_parents:
            self.send_parent_notification(report)
    
    def send_parent_notification(self, report):
        """Send notification to student's parents"""
        # This will be implemented in Phase 6 with Firebase
        pass


class PaymentRecordViewSet(viewsets.ModelViewSet):
    """ViewSet for payment records"""
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['payment_type', 'status', 'currency']
    search_fields = ['student__first_name', 'student__last_name', 'reference_number']
    
    def get_queryset(self):
        """Filter by school"""
        return PaymentRecord.objects.filter(student__school=self.request.user.school)
    
    def perform_create(self, serializer):
        """Create payment record with creator info"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def overdue_payments(self, request):
        """Get all overdue payments"""
        overdue_payments = self.get_queryset().filter(
            status='pending',
            due_date__lt=date.today()
        )
        serializer = self.get_serializer(overdue_payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def payment_summary(self, request):
        """Get payment summary statistics"""
        payments = self.get_queryset()
        
        summary = {
            'total_payments': payments.count(),
            'total_amount': payments.aggregate(total=Sum('amount'))['total'] or 0,
            'paid_amount': payments.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0,
            'pending_amount': payments.filter(status='pending').aggregate(total=Sum('amount'))['total'] or 0,
            'overdue_amount': payments.filter(status='overdue').aggregate(total=Sum('amount'))['total'] or 0,
            'payment_types': payments.values('payment_type').annotate(
                count=Count('id'),
                total_amount=Sum('amount')
            )
        }
        
        return Response(summary)
