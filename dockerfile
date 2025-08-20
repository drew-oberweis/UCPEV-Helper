FROM python:3.13
RUN mkdir /app

ADD admin_commands.py /app
ADD main.py /app
ADD requirements.txt /app
ADD user_commands.py /app
ADD utils.py /app
ADD data.py /app
ADD environment_handler.py /app
ADD update_handler.py /app
ADD ride.py /app
ADD route.py /app
ADD sheets_interface.py /app
ADD discord_main.py /app
ADD telegram_main.py /app
ADD message_queue.py /app
ADD location.py /app
ADD scheduled.py /app
ADD db.py /app
ADD task_schedulers.py /app

WORKDIR /app
RUN mkdir /app/logs
RUN pip install -r requirements.txt
CMD ["python", "-u", "main.py"]