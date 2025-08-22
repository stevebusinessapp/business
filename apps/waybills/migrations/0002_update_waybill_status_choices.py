# Generated manually for waybill status field updates
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('waybills', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='waybill',
            name='status',
            field=models.CharField(choices=[('delivered', 'Delivered'), ('pending', 'Pending'), ('processing', 'Processing'), ('dispatched', 'Dispatched / In Transit'), ('not_delivered', 'Not Delivered'), ('returned', 'Returned'), ('cancelled', 'Cancelled'), ('on_hold', 'On Hold'), ('awaiting_pickup', 'Awaiting Pickup')], default='pending', max_length=20),
        ),
    ]
