FROM nvcr.io/partners/gridai/pytorch-lightning:v1.4.0
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
RUN pip3 install opencv-python
RUN apt update
ENV DEBIAN_FRONTEND=noninteractive 
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY run.sh .
COPY main.py .
COPY yolov4.cfg cfg/
EXPOSE 8080
RUN sh run.sh
CMD ["python3","main.py"]
