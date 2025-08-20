from telegram.ext import Application
from collections.abc import Callable
import logging

logger = logging.getLogger(__name__)

global app

def define_app(application: Application):
    global app
    app = application

def add_scheduled_task(callback: Callable, interval: int, first: int = 0):
    """Add a scheduled task to the job queue."""
    if not callable(callback):
        raise ValueError("Callback must be a callable function.")
    app.job_queue.run_repeating(callback, interval=interval, first=first)

def add_single_task(callback: Callable, delay: int, data: dict = None):
    """Add a single task to the job queue."""
    if not callable(callback):
        raise ValueError("Callback must be a callable function.")
    app.job_queue.run_once(callback, when=delay, data=data)
    logger.debug(f"Scheduled single task: {callback.__name__} in {delay} seconds with data: {data}")