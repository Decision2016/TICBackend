FROM python:3.6
RUN mkdir -p /usr/src/app
COPY geckodriver /usr/bin/geckodriver
RUN chmod 111 /usr/bin/geckodriver
COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r /usr/src/app/requirements.txt
WORKDIR /usr/src/app
COPY . /usr/src/app