# Set base image (host OS)
FROM python:3.10-alpine

# set the virtual environment
RUN python -m venv venv

# Enable venv
ENV PATH="/venv/bin:$PATH"

# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app

# not working at the moment. Need to run it manually
#RUN pip freeze > ./requirements.txt

# copy requirements.txt to the /app folder
COPY requirements.txt .

# Install any dependencies using /app/requirements.txt
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY src/aws.py .
COPY src/functions.py .
COPY src/pdf.py .
COPY src/server.py .
COPY src/staticvars.py .
COPY src/users.py .

# copy folders into the working directory
COPY src/static         ./static/
COPY src/templates      ./templates/
COPY src/translations   ./translations/

# create the "config" folder under the "app" folder
RUN mkdir -p ./config

COPY config/config-prod.dat ./config/config.json

RUN cat ./config/config.json

# Specify the command to run on container start
# --error-logfile FILE (if flag not used, it spits to stderr by default)
# --log-level LEVEL (LEVEL can be 'debug', 'info', 'warning', 'error' or 'critical')
CMD ["gunicorn", "--workers=1", "--threads=4", "--keep-alive=65", "--bind=0.0.0.0:5000", "server:app"]
