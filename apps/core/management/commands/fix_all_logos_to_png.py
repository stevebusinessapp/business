from django.core.management.base import BaseCommand
import os
from PIL import Image

class Command(BaseCommand):
    help = 'Re-save all PNG files in media/company/logos/ as standard PNGs using Pillow.'

    def handle(self, *args, **options):
        base_dir = os.path.abspath(os.path.join('media', 'company', 'logos'))
        count = 0
        failed = 0
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.lower().endswith('.png'):
                    file_path = os.path.join(root, file)
                    try:
                        img = Image.open(file_path)
                        # Convert to RGBA if possible, else RGB
                        if img.mode not in ("RGBA", "RGB"):
                            img = img.convert("RGBA")
                        img.save(file_path, format='PNG')
                        count += 1
                        self.stdout.write(self.style.SUCCESS(f'Fixed: {file_path}'))
                    except Exception as e:
                        failed += 1
                        self.stdout.write(self.style.ERROR(f'Failed: {file_path} ({e})'))
        self.stdout.write(self.style.SUCCESS(f'Completed. {count} PNG files re-saved. {failed} failed.')) 