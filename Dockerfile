FROM firefox-python:18.04
COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt /usr/src/app/requirements.txt
RUN apt-get install python3-pip -y
RUN pip3 install -r /usr/src/app/requirements.txt
WORKDIR /usr/src/app
COPY . /usr/src/app