FROM python:3.9-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py ./
CMD ["python3", "./gazpar2mqtt.py", "--schedule", "04:00"]
