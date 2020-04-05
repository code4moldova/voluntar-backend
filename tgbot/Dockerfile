FROM python:3.8.2-slim

RUN mkdir /app
WORKDIR /app
ADD . /app

RUN pip install -r requirements.txt

EXPOSE 5001

CMD python main.py
