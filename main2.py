import os
import threading
import time
from cv2 import VideoCapture
import cv2
from flask import Flask, request, copy_current_request_context, send_file
# import sys, os
# sys.path.append(os.path.join(os.getcwd(),'python/'))
import darknet
import logging
from multiprocessing import Process, Pipe, Queue, set_start_method
import time
import subprocess
app = Flask(__name__)
# app.app_context().push()


# logging.basicConfig(filename='/record.log', level=logging.DEBUG)

def execute_trigger_command(command):
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output, error


def execute_curl_command(command: str):
    curl_command = f"curl http://192.168.2.2:1936/{command}"
    output, error = execute_trigger_command(curl_command)

    if output:
        print(f"Command output: {output.decode()}")
    if error:
        print(f"Command error: {error.decode()}")


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
    detections = darknet.detect_image(
        network, class_names, darknet_image, thresh=thresh)
    darknet.free_image(darknet_image)
    image = darknet.draw_boxes(detections, image_resized, class_colors)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), detections


@app.route('/api/stream/active/<source>/<int:time>', methods=['GET'])
def handle_streaming_active_thread_init(source, time):
    rtmp_streaming_url = source
    time_to_detect = time
    # detect_streaming(rtmp_streaming_url, time_to_detect)
    try:
        th = threading.Thread(target=detect_streaming, args=(
            rtmp_streaming_url, time_to_detect, ))
        th.start()
    except:
        print("error")

    return 'OK', 200


@app.route('/api/stream/<source>/<int:time>', methods=['GET'])
def handle_streaming_thread_init(source, time):
    rtmp_streaming_url = source
    time_to_detect = time
    try:
        th = threading.Thread(target=detect_streaming, args=(
            rtmp_streaming_url, time_to_detect,))
        th.start()
    except:
        print("error")
    th.join()
    return 'OK', 200


def detect_streaming(rtmp_streaming_url: str, time_to_detect: int):
    execute_curl_command('start_streaming')

    path = f"rtmp://{rtmp_streaming_url}/live/stream"
    cap = VideoCapture(path)
    t0 = time.monotonic()
    start_time = t0
    frame_count = 1
    frame_number = 0

    while (True):
        # print("\n===========================================================Count:" + str(count))
        ret, frame = cap.read()
        if ret == True:
            cv2.imwrite("frame.jpg", frame)
            frame_number += 1
            print("** HANDLE FRAME NUMBER : {}\n***TIMESTAMP: {}".format(
                frame_number, time.strftime("%Y%m%d-%H%M%S")))
            print("RESULTS:")
            image_name = 'frame.jpg'
            image, detections = image_detection(
                image_name, network, class_names, class_colors, 0.25
            )
            darknet.print_detections(detections, True)
            # r = dn.detect(net, meta, b'frame.jpg')

            # queue.put(detections)
            time.sleep(0)
            frame_count += 1
            td = time.monotonic() - t0
            if td > 1:
                current_fps = frame_count / td
                # logging.info('', extra={'fps': f'{current_fps:.2f}'})
                app.logger.info(f'{current_fps:.2f}')
                frame_count = 0
                t0 = time.monotonic()
            print()
            if not cap.isOpened() or time.monotonic() - start_time > time_to_detect:
                break
        else:
            print("No more frames. Exiting...")
            break

    cap.release()
    return


@app.route('/api/picture', methods=['POST'])
def handle_picture_api():
    @copy_current_request_context
    def handle_picture():
        f = request.files['upload']
        f.save(f.filename)
        preProcessingTime = time.time()
        image, detections = image_detection(
            f.filename, network, class_names, class_colors, 0.25)

        darknet.print_detections(detections, True)
        print("\nProcessing Time: "+str(time.time() - preProcessingTime))
    try:
        th = threading.Thread(target=handle_picture, args=())
        th.start()
        handle_picture()
    except:
        print("error")
    th.join()
    return 'OK', 200


@app.route('/api/picture/return', methods=['POST'])
def handle_picture_api_return():
    return_val_from_1 = []

    @copy_current_request_context
    def handle_picture_return():
        f = request.files['upload']
        f.save(f.filename)
        preProcessingTime = time.time()
        image, detections = image_detection(
            f.filename, network, class_names, class_colors, 0.25)
        return_val_from_1.append(
            str(darknet.print_detections_image_return(detections, True)))
        print("\nProcessing Time: "+str(time.time() - preProcessingTime))
        return_val_from_1.append("\n" +
                                 str(time.time() - preProcessingTime) + "\n")
    try:
        th = threading.Thread(target=handle_picture_return, args=())
        th.start()
        handle_picture_return()
    except:
        print("error")
    th.join()
    return ''.join(return_val_from_1), 200


@app.route('/api/picture/return/detection', methods=['POST'])
def handle_picture_api_return_detection():
    return_val_from_1 = []

    @copy_current_request_context
    def handle_picture_return_detection():
        f = request.files['upload']
        f.save(f.filename)
        preProcessingTime = time.time()
        image, detections = image_detection(
            f.filename, network, class_names, class_colors, 0.25)
        return_val_from_1.append(
            str(darknet.print_detections_image_detec_return(detections, True)))
    try:
        th = threading.Thread(target=handle_picture_return_detection, args=())
        th.start()
        handle_picture_return_detection()
    except:
        print("error")
    th.join()
    return ''.join(return_val_from_1), 200


@app.route('/api/active', methods=['GET'])
def active_process():
    return 'Active process', 200


@app.route('/api/terminate', methods=['GET'])
def terminate_process():
    global IS_TERMINATE
    IS_TERMINATE = True
    os._exit(0)
    return


@app.route('/download')
def downloadFile():
    path = "/record.log"
    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    network, class_names, class_colors = darknet.load_network(
        'cfg/yolov4-csp.cfg', 'cfg/coco.data', 'yolov4-csp.weights')
    # logging.basicConfig(filename='app.log', filemode='a', level=logging.INFO,
    #                 format='%(asctime)s - %(levelname)s - FPS: %(fps)s')
    # port = int(os.getenv('PORT', 8881))
    # app.run(port=port, host='0.0.0.0')
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
