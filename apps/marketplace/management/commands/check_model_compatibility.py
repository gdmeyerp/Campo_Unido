from django.core.management.base import BaseCommand
from django.db import connection
from apps.marketplace.models import MarketplaceProducto

class Command(BaseCommand):
    help = 'Checks model compatibility with the database'

    def handle(self, *args, **options):
        # Get model fields
        model_fields = [field.name for field in MarketplaceProducto._meta.get_fields()]
        
        # Get database columns
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA table_info(marketplace_marketplaceproducto)")
            db_columns = [col[1] for col in cursor.fetchall()]
        
        # Print results
        print("Model fields:")
        for field in model_fields:
            print(f"  - {field}")
        
        print("\nDatabase columns:")
        for column in db_columns:
            print(f"  - {column}")
        
        # Check for fields in model but not in database
        fields_not_in_db = [field for field in model_fields if field not in db_columns and not field.endswith('_set')]
        if fields_not_in_db:
            print("\nFields in model but not in database:")
            for field in fields_not_in_db:
                print(f"  - {field}")
        
        # Check for columns in database but not in model
        columns_not_in_model = [column for column in db_columns if column not in model_fields]
        if columns_not_in_model:
            print("\nColumns in database but not in model:")
            for column in columns_not_in_model:
                print(f"  - {column}") 