# Generated manually for status field updates
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('unpaid', 'Unpaid'), ('partial', 'Partially Paid'), ('paid', 'Paid'), ('delivered', 'Delivered')], default='unpaid', max_length=15),
        ),
    ]
