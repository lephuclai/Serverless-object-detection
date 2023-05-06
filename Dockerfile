FROM nvcr.io/nvidia/merlin/merlin-pytorch:23.04
RUN mkdir detection
COPY requirements.txt detection

RUN export LC_CTYPE=en_US.UTF-8
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
COPY run.sh .
COPY main.py .
RUN pip3 install opencv-python
RUN apt update
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
EXPOSE 8080
CMD ["sh","./run.sh"]