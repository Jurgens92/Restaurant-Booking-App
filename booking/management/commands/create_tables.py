from django.core.management.base import BaseCommand
from booking.models import Table

class Command(BaseCommand):
    help = 'Creates initial tables for the restaurant'

    def handle(self, *args, **options):
        table_data = [
            {'table_number': 1, 'capacity': 2, 'location': 'WINDOW'},
            {'table_number': 2, 'capacity': 2, 'location': 'WINDOW'},
            {'table_number': 3, 'capacity': 4, 'location': 'INSIDE'},
            {'table_number': 4, 'capacity': 4, 'location': 'INSIDE'},
            {'table_number': 5, 'capacity': 6, 'location': 'INSIDE'},
            {'table_number': 6, 'capacity': 8, 'location': 'BALCONY'},
            {'table_number': 7, 'capacity': 2, 'location': 'BAR'},
            {'table_number': 8, 'capacity': 2, 'location': 'BAR'},
        ]
        
        tables_created = 0
        
        for data in table_data:
            table, created = Table.objects.get_or_create(
                table_number=data['table_number'],
                defaults={
                    'capacity': data['capacity'],
                    'location': data['location']
                }
            )
            
            if created:
                tables_created += 1
                self.stdout.write(self.style.SUCCESS(f'Created table #{data["table_number"]}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {tables_created} tables'))