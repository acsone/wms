VERSION = None


def get_tasks():
    from . import tasks

    return tasks.tasks
