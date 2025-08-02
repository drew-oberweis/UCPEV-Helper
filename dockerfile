FROM python:3.13
RUN mkdir /app

ADD admin_commands.py /app
ADD main.py /app
ADD requirements.txt /app
ADD user_commands.py /app
ADD utils.py /app
ADD data.py /app
ADD environment_handler.py /app
ADD custom_handlers.py /app
ADD ride.py /app
ADD route.py /app
ADD sheets_interface.py /app

WORKDIR /app
RUN mkdir /app/logs
RUN pip install -r requirements.txt
CMD ["python", "main.py"]