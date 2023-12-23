FROM python:3.9-bullseye
WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY . /usr/src/app
RUN pip install -r requirements.txt
ENV FLASK_APP=app
CMD ["flask","run","--host","0.0.0.0","--port","8080"]