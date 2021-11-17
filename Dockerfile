FROM python:3.9.7-slim

COPY ./app /app

RUN apt-get update
RUN mkdir -p /data
RUN apt-get build-dep -y python3-lxml
RUN apt-get install -y libxml2-dev libxslt1-dev libxml2
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir -r /app/requirement.txt

CMD ["python3", "app/gazpar2mqtt.py"]
