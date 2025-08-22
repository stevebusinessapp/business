from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.utils import timezone

User = get_user_model()

class JobOrderLayout(models.Model):
    """
    Stores custom table layouts for each user or organization.
    """
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='joborder_layouts')
    organization = models.CharField(max_length=100, null=True, blank=True)
    structure = models.JSONField(help_text="List of columns/fields for the job order table.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class JobOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    title = models.CharField(max_length=200)
    layout = models.ForeignKey(JobOrderLayout, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_orders')
    data = models.JSONField(help_text="Dynamic table data: list of rows/fields.")
    summary = models.JSONField(null=True, blank=True, help_text="Auto-calculated summary figures (totals, etc.)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_joborders')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_joborders')
    organization = models.CharField(max_length=100, null=True, blank=True)
    tracking_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = [
            ("can_approve_joborder", "Can approve job orders"),
            ("can_view_all_joborders", "Can view all job orders"),
        ]

    def __str__(self):
        return f"JobOrder #{self.id} - {self.title}"

    def is_editable(self):
        return self.status in ['draft', 'submitted', 'pending']

    def can_approve(self):
        return self.status == 'pending'

    def save(self, *args, **kwargs):
        if not self.tracking_id:
            last = JobOrder.objects.order_by('-id').first()
            next_num = 1
            if last and last.tracking_id and last.tracking_id.startswith('JOB-'):
                try:
                    last_num = int(last.tracking_id.split('-')[-1])
                    next_num = last_num + 1
                except Exception:
                    pass
            self.tracking_id = f"JOB-{next_num:04d}"
        super().save(*args, **kwargs)

class JobOrderComment(models.Model):
    job_order = models.ForeignKey(JobOrder, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user} on JobOrder #{self.job_order_id}"
