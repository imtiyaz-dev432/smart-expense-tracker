from celery import Celery,Task #Celery ka base class — jo har task ka structure define karta hai. Task khud nahi banata

def make_celery(app):

    class FlaskTask(Task):
      def __call__(self,*args,**kwargs):
        with app.app_context():
            return self.run(*args,**kwargs)
    celery_app=Celery(
        app.import_name,
        broker=app.config.get("CELERY_BROKER_URL",   
            "redis://localhost:6379/1"
        ),
        backend=app.config.get(
            "CELERY_BROKER_URL",
            "redis://localhost:6379/2"
        ),
        task_cls=FlaskTask,
        include=["utils.otp"]
    )        
    celery_app.conf.timezone='Asia/Kolkata'
    return celery_app