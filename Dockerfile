FROM nvcr.io/nvidia/pytorch:21.10-py3
RUN mkdir detection
COPY requirements.txt detection

# RUN 
RUN python3 -m pip install --upgrade pip wheel --extra-index-url=https://pypi.ngc.nvidia.com --trusted-host pypi.ngc.nvidia.com

RUN export LC_CTYPE=en_US.UTF-8 &&\
    pip3 install Flask &&\
    pip3 install -r detection/requirements.txt

COPY setup.py detection
COPY yolov5n.pt detection
COPY yolo_detection.py detection
COPY run.sh detection

# RUN git clone https://github.com/ultralytics/yolov5
# RUN cd yolov5
# RUN pip3 install -r yolov5/requirements.txt


RUN python3 detection/setup.py
WORKDIR detection
# RUN python3 setup.py
RUN chmod +x run.sh
EXPOSE 8080
CMD ["sh","./run.sh"]