FROM alpine:latest

WORKDIR /usr/src/app
ADD https://certigna.tbs-certificats.com/wildca.crt /usr/local/share/ca-certificates
RUN update-ca-certificates

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY *.py ./
CMD ["python3", "./gazinflux.py", "--schedule", "06:00"]
