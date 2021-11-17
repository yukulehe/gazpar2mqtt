FROM python:3.9.7-slim

COPY ./app /app

RUN apt-get update
RUN mkdir -p /data
RUN apt-get build-dep -y python3-lxml
RUN apt-get install -y python3-lxml
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /app/requirement.txt

CMD ["python3", "app/gazpar2mqtt.py"]
