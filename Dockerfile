FROM python:3.9-slim-buster

COPY ./app /app

RUN apt-get update
RUN mkdir -p /data
RUN pip install --no-cache-dir -r /app/requirement.txt

CMD ["python3", ".app/gazpar2mqtt.py"]
