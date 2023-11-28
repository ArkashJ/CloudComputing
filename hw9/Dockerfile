ARG PYTHON_VERSION=3.11.4
FROM python:${PYTHON_VERSION}-slim as base

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY app.py .

EXPOSE 8080

CMD ["python3", "-m", "flask", "run", "--port=8080"]
