FROM nvcr.io/nvidia/l4t-pytorch:r32.7.1-pth1.9-py3
RUN mkdir detection
COPY requirements.txt detection

RUN export LC_CTYPE=en_US.UTF-8
RUN python3 -m pip install --upgrade pip wheel
RUN export LC_CTYPE=en_US.UTF-8 &&\
    pip3 install Flask &&\
    pip3 install -r detection/requirements.txt
# RUN pip3 install opencv-python==4.5.5.64
RUN pip3 install opencv-python==3.4.18.65
RUN mkdir detection/darknet
COPY darknet detection/darknet
WORKDIR detection/darknet
RUN make
COPY run.sh .
COPY main.py .
EXPOSE 8080
CMD ["sh","./run.sh"]