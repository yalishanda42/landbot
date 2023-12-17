# Python image to use.
FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY . .

ENTRYPOINT ["python", "app.py"]
