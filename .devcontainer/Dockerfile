FROM ubuntu:20.04
WORKDIR /
RUN apt-get -y update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata
RUN apt-get install -y python3 python3-dev git python3-pip python3-kivy python-is-python3 libgl1-mesa-dev build-essential
RUN ln -s $(which pip3) /usr/bin/pip
RUN pip install pymongo pandas numpy scipy scikit-learn matplotlib pylint kivy