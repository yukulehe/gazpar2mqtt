FROM python:3.9.7-slim

COPY ./app /app

RUN apt-get update
RUN mkdir -p /data

# Prerequisite for installing package lxml on armv7
RUN apt-get install --upgrade -y g++ gcc libxml2-dev libxslt-dev python3-dev
 
# Install python requirements
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r /app/requirement.txt

CMD ["python3", "app/gazpar2mqtt.py"]
