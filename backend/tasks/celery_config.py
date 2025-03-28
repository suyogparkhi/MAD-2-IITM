from celery import Celery
from flask import Flask
import os 

def make_celery(app=None):

    celery = Celery(
        'household_services',
        broker = os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        backend = os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        include = ['tasks.scheduled_tasks', 'tasks.report_tasks' , 'tasks.export_tasks']
    )

    if app:
        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args,**kwargs)
        
        celery.Task = ContextTask

    
    celery.conf.beat_schedule = {
        'daily-reminders': {
            'task': 'tasks.scheduled_tasks.send_daily_reminders',
            'schedule' : 30
        },
         'monthly-reports': {
            'task': 'tasks.report_tasks.generate_monthly_reports',
            'schedule': 30.0,
            'options': {'day_of_month': 1} 
        },
    }

    return celery