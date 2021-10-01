FROM python:3.9-slim-buster

COPY ./app /app

RUN mkdir -p /data
RUN pip install -r /app/requirement.txt

CMD ["python3", ".app/gazpar2mqtt.py"]
