from celery import Task

from stt.db.database import SessionLocal


class SqlAlchemyTask(Task):
    """
    Abstract base class for Celery tasks that use SqlAlchemy
    """

    db = None

    def before_start(self, task_id, args, kwargs):
        self.db = SessionLocal()
        return super().before_start(task_id, args, kwargs)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        self.db.close()  # type: ignore
        return super().after_return(status, retval, task_id, args, kwargs, einfo)
