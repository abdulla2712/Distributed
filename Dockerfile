FROM python:3.11.1

# Force the stdout and stderr streams to be unbuffered.
ENV PYTHONUNBUFFERED 1
# If given, Python won’t try to write .pyc files on the import of source modules.
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /app/
