FROM python:3.9.7-slim

COPY ./app /app

RUN apt-get update && \
    apt-get install -y locales git && \
    sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    rm -rf /var/lib/apt/lists/*
    
RUN mkdir -p /data

ENV LANG fr_FR.UTF-8
ENV LC_ALL fr_FR.UTF-8
ENV TZ=Europe/Paris

# Prerequisite for installing package lxml on armv7
#RUN apt-get install --upgrade -y g++ gcc libxml2-dev libxslt-dev python3-dev
 
# Install python requirements
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r /app/requirement.txt

CMD ["python3", "app/gazpar2mqtt.py"]
