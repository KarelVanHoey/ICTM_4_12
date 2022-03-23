import time
import threading
import bluetooth
import keyboard
# example of two threads, one to listen, one to send

exitFlag = 0

class ServerSendThread(threading.Thread):

    def __init__(self, name, port):
        threading.Thread.__init__(self)
        self.name = name
        self.port = port

    def run(self):
        print("Starting sending as server: " + self.name)
        server_send(self.name, self.port)
        print("Stopping sending as server: " + self.name)


class ServerReceiveThread(threading.Thread):

    def __init__(self, name, port):
        threading.Thread.__init__(self)
        self.name = name
        self.port = port

    def run(self):
        print("Starting receiving as server: " + self.name)
        server_receive(self.name, self.port)
        print("Stopping receiving as server: " + self.name)


def server_send(threadName, port):
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port)) # same port as the receiving port on the ev3-brick
    server_sock.listen(1)  # listen for a connection
    client_sock, address = server_sock.accept()  # accept the connection
    print("Accepted connection from ", address)
    while exitFlag == 0:
        if keyboard.is_pressed('z'):
            message = 'forward'
        elif keyboard.is_pressed('q'):
            message = 'left'
        elif keyboard.is_pressed('d'):
            message = 'right'
        elif keyboard.is_pressed('s'):
            message = 'back'
        else:
            message = 'stop'
        message_as_bytes = str.encode(message)
        client_sock.send(message_as_bytes)
        time.sleep(0.1)
    print("stopping thread " + threadName)


def server_receive(threadName, port):
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    server_sock.bind(("", port))
    server_sock.listen(1)  # listen for a connection
    client_sock, address = server_sock.accept()  # accept the connection
    print("Accepted connection from ", address)
    while exitFlag == 0:
        message_as_bytes = client_sock.recv(1024)  # wait for answer
        message = message_as_bytes.decode()
        print(message)
    print("stopping thread " + threadName)


sendport = 28
receiveport = 29

# Create new threads
thread1 = ServerSendThread("sendthread", sendport)
thread2 = ServerReceiveThread("receivethread", receiveport)

# Start new Threads
thread1.start()
thread2.start()
