from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('receipts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='receipt',
            name='received_by',
            field=models.CharField(max_length=255),
        ),
    ] 