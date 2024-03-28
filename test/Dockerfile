#FROM nvcr.io/nvidia/merlin/merlin-pytorch:23.04
FROM ubuntu:20.04

COPY requirements.txt .


RUN export LC_CTYPE=en_US.UTF-8

RUN apt-get update && \
    apt-get install sudo && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install wget && \
    apt install -y python3.8


RUN apt-get update && apt-get install curl -y
RUN apt install python3-pip -y

RUN python3 -m pip install --upgrade pip wheel
RUN export LC_CTYPE=en_US.UTF-8 &&\
    pip3 install Flask &&\
    pip3 install -r requirements.txt

RUN pip3 install -U numpy
RUN apt update


# Change
COPY main.py .

EXPOSE 8080

# Change
CMD ["python3","main.py"]
