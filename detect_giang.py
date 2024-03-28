import subprocess
import threading
import time
from multiprocessing import Process, Pipe

def execute_kubectl_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output, error

def execute_curl_command(ip, port, time_detect, count):
    # curl_command = f"kubectl exec -it ubuntu -- curl http://detection1.serverless.svc.cluster.local/api/stream/active/{ip}:{port}/{time_detect}/{count}"
    # curl_command = f"curl http://172.16.42.12:8080/api/stream/{ip}:{port}/{time_detect}/0"
    curl_command = f"curl http://172.16.42.12:8080/api/stream/active/{ip}:{port}/{time_detect}/{count}"
    output, error = execute_kubectl_command(curl_command)

    if output:
        print(f"Command output: {output.decode()}")
    if error:
        print(f"Command error: {error.decode()}")

def main():
    # Thông số của câu lệnh curl
    ip = "192.168.2.2"
    start_port = 1935
    # start_port = 12345
    num_threads = 2 # Số lượng luồng
    time_detect = 200
    count = 0

    # Tạo và khởi chạy các luồng
    threads = []
    for i in range(num_threads):
        port = start_port
        count = count + 1
        # time_detect = time_detect + i*100
        thread = Process(target=execute_curl_command, args=(ip, port, time_detect, count))
        threads.append(thread)
        thread.start()

    # Chờ tất cả các luồng hoàn thành
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
