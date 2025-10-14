from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.functions import TruncDate

from apps.job.models import AccuracyMetrics, JobApplications

@receiver(post_save, sender=JobApplications)
def update_accuracy_on_status_change(sender, instance, **kwargs):

    if not instance.created_at:
        return
    
    post_date = instance.created_at.date()

    apps_same_date = JobApplications.objects.filter(
        created_at__date=post_date
    )

    if not apps_same_date.exists():
        return

    metric, _ = AccuracyMetrics.objects.get_or_create(interview_date=post_date)
    metric.job_applications.set(apps_same_date)
    metric.calculate_metrics()

