from celery import Celery

celery_app = Celery("data_processing_tasks", broker='pyamqp://guest@localhost//')

@celery_app.task
def some_function():
    return "test values"