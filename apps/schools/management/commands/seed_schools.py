from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.schools.models import School, SchoolConfiguration
from apps.authentication.models import User
import random


class Command(BaseCommand):
    help = 'Seed sample schools for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=5,
            help='Number of schools to create'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Sample school data
        schools_data = [
            {
                'name': 'École Primaire Publique de Niamey',
                'school_type': 'primary',
                'city': 'Niamey',
                'state': 'Niamey',
                'contact_email': 'contact@epp-niamey.ne',
                'contact_phone': '+22790123456',
                'address': 'Quartier Plateau, Niamey, Niger'
            },
            {
                'name': 'Lycée Technique National',
                'school_type': 'secondary',
                'city': 'Niamey',
                'state': 'Niamey',
                'contact_email': 'info@ltn-niamey.ne',
                'contact_phone': '+22790123457',
                'address': 'Zone Industrielle, Niamey, Niger'
            },
            {
                'name': 'Collège Privé Sainte Marie',
                'school_type': 'both',
                'city': 'Maradi',
                'state': 'Maradi',
                'contact_email': 'admin@cpsm-maradi.ne',
                'contact_phone': '+22790123458',
                'address': 'Centre-ville, Maradi, Niger'
            },
            {
                'name': 'École Secondaire de Zinder',
                'school_type': 'secondary',
                'city': 'Zinder',
                'state': 'Zinder',
                'contact_email': 'contact@esz-zinder.ne',
                'contact_phone': '+22790123459',
                'address': 'Quartier Birni, Zinder, Niger'
            },
            {
                'name': 'Institut Supérieur de Formation',
                'school_type': 'university',
                'city': 'Agadez',
                'state': 'Agadez',
                'contact_email': 'info@isf-agadez.ne',
                'contact_phone': '+22790123460',
                'address': 'Campus Universitaire, Agadez, Niger'
            }
        ]
        
        created_schools = []
        
        for i, school_data in enumerate(schools_data[:count]):
            school = School.objects.create(
                name=school_data['name'],
                school_type=school_data['school_type'],
                city=school_data['city'],
                state=school_data['state'],
                contact_email=school_data['contact_email'],
                contact_phone=school_data['contact_phone'],
                address=school_data['address'],
                is_verified=True
            )
            
            # Create school configuration
            SchoolConfiguration.objects.create(
                school=school,
                academic_year_start=timezone.now().date().replace(month=9, day=1),
                academic_year_end=timezone.now().date().replace(month=6, day=30),
                current_semester='first',
                currency='NGN',
                payment_reminder_days=7,
                max_file_size_mb=10,
                allowed_file_types=['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            )
            
            created_schools.append(school)
            self.stdout.write(
                self.style.SUCCESS(f'Created school: {school.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_schools)} schools')
        ) 