import os
import threading
import time
from cv2 import VideoCapture
import cv2
from flask import Flask
# import sys, os
# sys.path.append(os.path.join(os.getcwd(),'python/'))
import darknet 


app = Flask(__name__)

def load_images(images_path):
    """
    If image path is given, return it directly
    For txt file, read it and return each line as image path
    In other case, it's a folder, return a list with names of each
    jpg, jpeg and png file
    """
    input_path_extension = images_path.split('.')[-1]
    if input_path_extension in ['jpg', 'jpeg', 'png']:
        return [images_path]
    elif input_path_extension == "txt":
        with open(images_path, "r") as f:
            return f.read().splitlines()
    else:
        return glob.glob(
            os.path.join(images_path, "*.jpg")) + \
            glob.glob(os.path.join(images_path, "*.png")) + \
            glob.glob(os.path.join(images_path, "*.jpeg"))

def image_detection(image_or_path, network, class_names, class_colors, thresh):
    # Darknet doesn't accept numpy images.
    # Create one with image we reuse for each detect
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    darknet_image = darknet.make_image(width, height, 3)
    image = cv2.imread(image_or_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height),
                               interpolation=cv2.INTER_LINEAR)

    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh)
    darknet.free_image(darknet_image)
    image = darknet.draw_boxes(detections, image_resized, class_colors)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), detections


@app.route('/api/stream/<source>/<int:time>', methods=['GET'])
def handle_streaming_thread_init(source, time):
    rtmp_streaming_url = source
    time_to_detect = time
    try:
        th = threading.Thread(target=detect_streaming, args=(
            rtmp_streaming_url,time_to_detect,))
        th.start()
    except:
        print("error")
    th.join()
    return 'OK', 200


def detect_streaming(rtmp_streaming_url: str, time_to_detect: int):
    path = f"rtmp://{rtmp_streaming_url}/live/stream"
    cap = VideoCapture(path)
    start_time = time.monotonic()
    frame_number = 0
    while (True):
        ret, frame = cap.read()
        if ret == True:
            cv2.imwrite("frame.jpg", frame)
            frame_number += 1
            print("** HANDLE FRAME NUMBER : {}\n***TIMESTAMP: {}".format(
                frame_number,time.strftime("%Y%m%d-%H%M%S")))
            print("RESULTS:")
            image_name = 'frame.jpg'
            image, detections = image_detection(
                    image_name, network, class_names, class_colors, 0.25
            )
            darknet.print_detections(detections, True)
            # r = dn.detect(net, meta, b'frame.jpg')
            # print(r)

            print()        
            if time.monotonic() - start_time > time_to_detect:
                break
    cap.release()
    return

@app.route('/api/active', methods=['GET'])
def active_process():
    return 'Active process', 200


@app.route('/api/terminate', methods=['GET'])
def terminate_process():
    global IS_TERMINATE
    IS_TERMINATE = True
    os._exit(0)
    return


if __name__ == '__main__':
    network, class_names, class_colors = darknet.load_network('cfg/yolov4.cfg','cfg/coco.data','yolov4.weights')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
