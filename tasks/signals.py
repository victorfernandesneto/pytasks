from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import timedelta
from tasks.models import Task
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from tasks.utils import notify_task


scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

@receiver(post_save, sender=Task)
def schedule_and_notify(sender, created, instance, **kwargs):
    job_id = f"notification_{instance.pk}"

    if created:
        # Schedule a new job
        scheduler.add_job(
            notify_task,
            'date',
            run_date=instance.deadline - timedelta(hours=1),
            id=job_id,
            replace_existing=True,
            args=[instance.pk]
        )
    else:
        # For existing tasks, modify the job
        job = scheduler.get_job(job_id)
        if job:
            job.modify(
                next_run_time=instance.deadline - timedelta(hours=1)
            )
        else:
            # If job doesn't exist, create a new one
            scheduler.add_job(
                notify_task,
                'date',
                run_date=instance.deadline - timedelta(hours=1),
                id=job_id,
                replace_existing=True,
                args=[instance.pk]
            )

scheduler.start()
