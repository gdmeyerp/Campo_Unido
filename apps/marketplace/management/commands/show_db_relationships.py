from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps

class Command(BaseCommand):
    help = 'Shows foreign key relationships in the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Showing database foreign key relationships...'))
        
        # Get all app labels
        app_labels = set(app.label for app in apps.get_app_configs())
        
        for app_label in sorted(app_labels):
            self.stdout.write(self.style.SUCCESS(f"\n=== {app_label.upper()} ==="))
            
            # Get models for this app
            models = apps.get_app_config(app_label).get_models()
            
            for model in models:
                model_name = model.__name__
                table_name = model._meta.db_table
                self.stdout.write(f"\nModel: {model_name} (Table: {table_name})")
                
                # Get fields for this model
                fields = model._meta.get_fields()
                foreign_key_fields = [f for f in fields if f.is_relation and f.many_to_one]
                
                if foreign_key_fields:
                    self.stdout.write("  Foreign Key Fields:")
                    for field in foreign_key_fields:
                        related_model = field.related_model.__name__
                        self.stdout.write(f"  - {field.name} → {related_model}")
                
                # Find models that reference this model
                relations_to_this_model = []
                for other_app_label in app_labels:
                    other_models = apps.get_app_config(other_app_label).get_models()
                    for other_model in other_models:
                        other_fields = other_model._meta.get_fields()
                        for field in other_fields:
                            if hasattr(field, 'related_model') and field.related_model == model:
                                relations_to_this_model.append((other_model.__name__, field.name))
                
                if relations_to_this_model:
                    self.stdout.write("  Referenced by:")
                    for other_model_name, field_name in relations_to_this_model:
                        self.stdout.write(f"  - {other_model_name}.{field_name}")
                
                # Count records
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        self.stdout.write(f"  Records: {count}")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"  Error counting records: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS('\nAnalysis completed.')) 