FROM python:3.7.1

LABEL Author="Serghei Ungurean"
LABEL E-mail="s.ungurean28@gmail.com"
LABEL version="0.1"

ENV PYTHONDONTWRITEBYTECODE 1
ENV FLASK_APP "backend/app.py"
ENV FLASK_ENV "development"
ENV FLASK_DEBUG True

RUN mkdir /app
WORKDIR /app

COPY Pip* /app/

RUN pip install --upgrade pip && \
    pip install 'pipenv==2018.11.26' && \
    pipenv install --dev --system --skip-lock

ADD . /app

RUN pip install dnspython 
RUN pip install sendgrid

EXPOSE 5000

CMD flask run --host=0.0.0.0
