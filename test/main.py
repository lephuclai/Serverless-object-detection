from flask import Flask, jsonify
import multiprocessing
import requests
import time

app = Flask(__name__)

start_curl = multiprocessing.Value('b', False)
response_time = multiprocessing.Value('d', 0.0)

@app.route('/api/start', methods=['GET'])
def start():
    global start_curl
    with start_curl.get_lock():
        start_curl.value = True
    return 'Started', 200

@app.route('/api/active', methods=['GET'])
def active_process():
    return 'Active process', 200

@app.route('/api/response_time', methods=['GET'])
def get_response_time():
    global response_time
    with response_time.get_lock():
        return jsonify(response_time=response_time.value)

def program_1():
    app.run(port=8080)

def program_2():
    global start_curl, response_time
    while True:
        with start_curl.get_lock():
            if start_curl.value:
                start_time = time.time()
                response = requests.get('http://localhost:8080/api/active')
                end_time = time.time()
                with response_time.get_lock():
                    response_time.value = end_time - start_time
                start_curl.value = False

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=program_1)
    p2 = multiprocessing.Process(target=program_2)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
