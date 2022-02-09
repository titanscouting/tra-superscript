FROM python:slim
WORKDIR /
RUN apt-get -y update; apt-get -y upgrade
RUN apt-get -y install git
COPY requirements.txt .
RUN pip install -r requirements.txt