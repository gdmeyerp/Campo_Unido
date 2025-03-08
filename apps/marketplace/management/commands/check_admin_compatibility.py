from django.core.management.base import BaseCommand
from django.contrib import admin
from django.db.models import fields as model_fields
from apps.marketplace.models import CategoriaProducto, MarketplaceProducto
from apps.marketplace.admin import CategoriaProductoAdmin, MarketplaceProductoAdmin

class Command(BaseCommand):
    help = 'Checks admin configuration for compatibility with models'

    def check_admin_field_compatibility(self, model, admin_class):
        self.stdout.write(f"\nChecking admin configuration for {model.__name__}:")
        
        # Get model fields
        model_field_names = [field.name for field in model._meta.get_fields()]
        
        # Check list_display
        if hasattr(admin_class, 'list_display'):
            self.stdout.write("  - list_display:")
            for field in admin_class.list_display:
                if callable(getattr(admin_class, field, None)):
                    self.stdout.write(f"    ✓ {field} (callable)")
                elif field in model_field_names:
                    self.stdout.write(f"    ✓ {field} (field)")
                else:
                    self.stdout.write(self.style.ERROR(f"    ✗ {field} (not found)"))
        
        # Check list_filter
        if hasattr(admin_class, 'list_filter') and admin_class.list_filter:
            self.stdout.write("  - list_filter:")
            for field in admin_class.list_filter:
                if field in model_field_names:
                    self.stdout.write(f"    ✓ {field} (field)")
                else:
                    self.stdout.write(self.style.ERROR(f"    ✗ {field} (not found)"))
        
        # Check prepopulated_fields
        if hasattr(admin_class, 'prepopulated_fields') and admin_class.prepopulated_fields:
            self.stdout.write("  - prepopulated_fields:")
            for target, sources in admin_class.prepopulated_fields.items():
                if target in model_field_names:
                    self.stdout.write(f"    ✓ {target} (target field)")
                else:
                    self.stdout.write(self.style.ERROR(f"    ✗ {target} (target not found)"))
                
                for source in sources:
                    if source in model_field_names:
                        self.stdout.write(f"    ✓ {source} (source field)")
                    else:
                        self.stdout.write(self.style.ERROR(f"    ✗ {source} (source not found)"))
        
        # Check fieldsets
        if hasattr(admin_class, 'fieldsets') and admin_class.fieldsets:
            self.stdout.write("  - fieldsets:")
            for name, options in admin_class.fieldsets:
                self.stdout.write(f"    Fieldset: {name}")
                for field in options.get('fields', []):
                    if isinstance(field, tuple):
                        for subfield in field:
                            if subfield in model_field_names:
                                self.stdout.write(f"      ✓ {subfield} (field)")
                            else:
                                self.stdout.write(self.style.ERROR(f"      ✗ {subfield} (not found)"))
                    else:
                        if field in model_field_names:
                            self.stdout.write(f"      ✓ {field} (field)")
                        else:
                            self.stdout.write(self.style.ERROR(f"      ✗ {field} (not found)"))

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking admin configuration compatibility...'))
        
        # Get actual admin instances
        categoria_admin = CategoriaProductoAdmin(CategoriaProducto, admin.site)
        producto_admin = MarketplaceProductoAdmin(MarketplaceProducto, admin.site)
        
        self.check_admin_field_compatibility(CategoriaProducto, categoria_admin)
        self.check_admin_field_compatibility(MarketplaceProducto, producto_admin)
        
        self.stdout.write(self.style.SUCCESS('\nCheck completed.')) 