import base64, ssl, subprocess, threading, time
from socketIO_client import SocketIO, LoggingNamespace
from numpy import fromstring, uint8
import json

class SpeechToTextClient():
    def __init__(self):
        print('Init speech to text client')
        self.socket_url = "cognigy-stts.northeurope.cloudapp.azure.com"
        self.socket_port = 3002
        self.listening = False
        self.firstByte = True
        self.waitResult = True
        self.waitResultBrain = True
        self.config = '{"servicename": "google", "sample_rate": 22000}'
        self.socketIO = SocketIO(self.socket_url, self.socket_port, LoggingNamespace, params={'noTts': True})

        # bind events
        # bind only 1 event since python socket io wait only waits for 1 event
        #self.socketIO.on('stt', self.received_message)
        self.socketIO.on('brain_output', self.received_message_brain)

        # wait for brain first reply
        while self.waitResultBrain:
            self.socketIO.wait(10)

        # audio threading
        self.stream_audio_thread = threading.Thread(target=self.stream_audio)
        self.stream_audio_thread.start()
        self.counter = 0

    def received_message(self, message):
        # on message received, stop waiting
        print "Message received: " + str(message)
        self.waitResult = False
        self.listening = False
        self.counter = 0
        self.wait_for_input()

    def received_message_brain(self, message):
        # on receiving message from brain, stop waiting
        print "Brain reply received: " + str(message)
        self.waitResultBrain = False
        self.listening = False
        self.counter = 0
        self.wait_for_input()

    def wait_for_input(self):
        # wait for keyboard signal to start recording
        self.firstByte = True
        print('Listening to input')
        key_input = raw_input('Press enter to record...')
        if(key_input):
            print('Input detected')
            self.listening = True
            self.stream_audio()

    def stream_audio(self):
        # start audio stream
        self.waitResult = True
        self.waitResultBrain = True

        # create new subprocess for arecord
        print('Stream audio')
        reccmd = ["arecord", "-c", "1", "-D", "plughw:1,0", "-f", "S16_LE", "-r", "22000", "-t", "wav"]
        p = subprocess.Popen(reccmd, stdout=subprocess.PIPE)

        # loop read stream while still listening
        while self.listening:
            self.counter += 1
            
            if(self.counter >= 100):
                print('Chunk end signal')
                self.socketIO.emit('stt_chunk_end')
                p.kill()
                self.firstByte = False
                self.listening = False
                print("Wait for result")

                while self.waitResultBrain:
                    print('waiting')
                    self.socketIO.wait(10)

            # read stream chunk and convert to binary array
            data = p.stdout.read(1024)
            data_bytes = fromstring(data, dtype=uint8)
            data_array = data_bytes.tolist()
            print(str(self.counter) + ' - ' + str(len(data_array)))
            
            if(self.firstByte):
                # if its first byte, send stt chunk start signal
                self.socketIO.emit('stt_chunk_start', self.config)
                self.firstByte = False
            
            # send audio chunk
            self.socketIO.emit('stt_chunk', data_array, self.counter)

print 'Stream python'
stt_client = SpeechToTextClient()
stt_client.wait_for_input()