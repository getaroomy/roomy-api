FROM python:3.8

## Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install Python Packages
RUN pip install -r requirements.txt

# Run gunicorn bound to the 8080 port.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --preload main:app