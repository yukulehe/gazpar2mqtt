FROM python:3.9.7-slim

COPY ./app /app

RUN apt-get update
RUN mkdir -p /data
RUN apt-get install -y libxml2 
RUN apt-get install -y libxslt1
RUN pip3 install --no-cache-dir -r /app/requirement.txt

CMD ["python3", "app/gazpar2mqtt.py"]
