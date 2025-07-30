from celery import Celery

celery=Celery("Application Jobs")

class ContextTask(celery.Task):
    def __call__(self,*args,**kwargs):
        with app.app_context():
            return super().__call__(*args,*kwargs)
            
celery.Task = ContextTask

def register_tasks():
    import backend.tasks

register_tasks()