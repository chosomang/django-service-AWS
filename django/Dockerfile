FROM python:3.8

WORKDIR /app

COPY entrypoint.sh /app/entrypoint.sh
COPY requirements.txt /app/

RUN chmod +x /app/entrypoint.sh
RUN pip install -r requirements.txt