FROM ubuntu:22.04
RUN apt -y update 
RUN apt -y upgrade 
WORKDIR /home
COPY . .
RUN rm Dockerfile
RUN rm -r migrations
RUN apt -y install tzdata
RUN apt -y update 
RUN apt -y install python3
RUN apt -y update 
RUN apt -y install python3-setuptools
RUN apt -y update 
RUN apt -y install python3-pip
RUN apt -y update 
RUN apt -y install postgresql 
RUN apt -y update 
RUN pip3 install pip-upgrader
RUN pip-upgrade -p all --skip-package-installation
RUN pip3 install -r requirements.txt
RUN rm requirements.txt
ENTRYPOINT python3 server.py
