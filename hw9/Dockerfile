ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION}-slim as base

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY main.py .

CMD flask --app main run --host=127.0.0.1 --port=8000
