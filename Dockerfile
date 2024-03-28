#FROM nvcr.io/nvidia/merlin/merlin-pytorch:23.04
FROM ubuntu:20.04

# # Giang
ENV PORT=8881

RUN mkdir detection
COPY requirements.txt detection


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
    pip3 install -r detection/requirements.txt
# RUN pip3 install opencv-python==4.5.5.64
# RUN pip3 install opencv-python
RUN pip3 install -U numpy
RUN mkdir detection/darknet
COPY darknet detection/darknet
WORKDIR detection/darknet
RUN make
RUN pip3 install opencv-python
RUN apt update
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY run.sh .

# Change
COPY main.py .


COPY yolov4.cfg cfg/
# EXPOSE 8080

EXPOSE $PORT

RUN sh run.sh
# Change
CMD ["python3","main.py"]
