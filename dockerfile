FROM python:3.13
RUN mkdir /app

ADD admin_commands.py /app
ADD main.py /app
ADD requirements.txt /app
ADD simple_commands.py /app
ADD utils.py /app
ADD data.py /app
ADD db.py /app
ADD environment_handler.py /app
ADD custom_handlers.py /app
ADD ride_convo_handlers.py /app
ADD ride.py /app
ADD flask_listener.py /app

# Open port 5000 for the Flask app
EXPOSE 5000

WORKDIR /app
RUN mkdir /app/logs
RUN pip install -r requirements.txt
CMD ["python", "main.py"]