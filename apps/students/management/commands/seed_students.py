from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.schools.models import School
from apps.students.models import Student, ParentStudent
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Seed sample students for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--school-id',
            type=str,
            help='Specific school ID to seed students for'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of students to create per school'
        )

    def handle(self, *args, **options):
        count = options['count']
        school_id = options['school_id']
        
        if school_id:
            schools = School.objects.filter(id=school_id)
        else:
            schools = School.objects.filter(is_active=True)
        
        if not schools.exists():
            self.stdout.write(
                self.style.ERROR('No active schools found')
            )
            return
        
        # Sample names for students
        first_names = [
            'Amina', 'Fatima', 'Hassan', 'Ibrahim', 'Mariam',
            'Omar', 'Zara', 'Yusuf', 'Aisha', 'Mohammed',
            'Khadija', 'Ali', 'Hawa', 'Abdullah', 'Safiya',
            'Ahmed', 'Fadima', 'Moussa', 'Hadjara', 'Boubacar'
        ]
        
        last_names = [
            'Diallo', 'Traore', 'Keita', 'Cisse', 'Konate',
            'Soumaoro', 'Coulibaly', 'Diakite', 'Sidibe', 'Toure',
            'Camara', 'Bah', 'Barry', 'Balde', 'Sylla',
            'Kone', 'Sangare', 'Diarra', 'Fofana', 'Kante'
        ]
        
        class_levels = [
            'Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5',
            'Class 6', 'Form 1', 'Form 2', 'Form 3', 'Form 4',
            'Form 5', 'Form 6'
        ]
        
        created_students = []
        
        for school in schools:
            self.stdout.write(f'Creating students for {school.name}...')
            
            for i in range(count):
                # Generate student data
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                student_id = f"{school.slug.upper()}{random.randint(1000, 9999)}"
                
                # Random birth date (5-18 years old)
                years_old = random.randint(5, 18)
                birth_date = date.today() - timedelta(days=years_old * 365)
                
                # Random enrollment date (within last 3 years)
                enrollment_days_ago = random.randint(0, 1095)
                enrollment_date = date.today() - timedelta(days=enrollment_days_ago)
                
                student = Student.objects.create(
                    school=school,
                    first_name=first_name,
                    last_name=last_name,
                    student_id=student_id,
                    class_level=random.choice(class_levels),
                    date_of_birth=birth_date,
                    gender=random.choice(['male', 'female']),
                    enrollment_date=enrollment_date,
                    is_active=random.choice([True, True, True, False])  # 75% active
                )
                
                created_students.append(student)
                
                if i % 10 == 0:
                    self.stdout.write(f'Created {i+1} students...')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_students)} students')
        ) 