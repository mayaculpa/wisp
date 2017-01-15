import RPi.GPIO as GPIO
import time
import subprocess
import datetime
import time

# Added to support voice command
import threading
import speech_recognition as sr

STATE_UNOCCUPIED = 0
STATE_OCCUPIED = 1
OCCUPIED_DISTANCE = 50
UNOCCUPIED_DURATION = 1200

def process_command(self, command):

    if command.lower() == "snap camera one":
        take_webcam_still()

    if command.lower() == "roll camera one":
        take_webcam_video()

    if command.lower() == "snap camera two":
        take_picam_still()

    if command.lower() == "roll camera two":
        take_picam_video()


Added to support voice command
class VoiceCommand(object):
    def __init__(self, interval=1):
        """ Constructor
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval
        self.parent_function = None
        thread = threading.Thread(target=self.init_speech_recognition, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()

    def set_command(self, func):
        self.parent_function = func

    def init_speech_recognition(self):
        # this is called from the background thread
        def callback(recognizer, audio):
            # received audio data, now we'll recognize it using Google Speech Recognition
            try:
                # for testing purposes, we're just using the default API key
                # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
                # instead of `r.recognize_google(audio)`
                command = recognizer.recognize_google(audio)
                #print("Google Speech Recognition thinks you said " + command)
                self.parent_function(command)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

        r = sr.Recognizer()
        m = sr.Microphone()
        with m as source:
            r.adjust_for_ambient_noise(source) # we only need to calibrate once, before we start listening

        # start listening in the background (note that we don't have to do this inside a `with` statement)
        stop_listening = r.listen_in_background(m, callback)
        # `stop_listening` is now a function that, when called, stops background listening

        # do some other computation for 5 seconds, then stop listening and keep doing other computations
        
        #for _ in range(50): time.sleep(0.1) # we're still listening even though the main thread is doing other things
        #stop_listening() # calling this function requests that the background listener stop listening
        while True: time.sleep(0.025)


def check_proximity():
    TRIG = 23 
    ECHO = 24

    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)

    GPIO.output(TRIG, False)
    time.sleep(1)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO)==0:
      pulse_start = time.time()

    while GPIO.input(ECHO)==1:
      pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

def take_webcam_still():
    subprocess.call(["fswebcam", "-p", "YUYV", "-d", "/dev/video0", "-r", "1024x768", "--top-banner", '"Volunder Waycraft"', "image.jpg"])

def take_webcam_video():
    subprocess.call(["fswebcam", "-p", "YUYV", "-d", "/dev/video0", "-r", "1024x768", "--top-banner", '"Volunder Waycraft"', "image.jpg"])

def take_picam_still():
    subprocess.call(["raspistill", "-o", "image.jpg"])

def take_picam_video():
    subprocess.call(["raspivid", "-o", "video.h264"])

def say(content):
    subprocess.call(["mpg123", content])    

#fswebcam -p YUYV -d /dev/video0 -r 1024x768 --top-banner --title "The Garage" --subtitle "tyler" --info "hello" image.jpg


def main(argv):
    state = STATE_UNOCCUPIED

    unoccupied_start = time.time()
    GPIO.setmode(GPIO.BCM)

    logger_level = logging.DEBUG
    logger = logging.getLogger('shop_log')
    logger.setLevel(logger_level)

    # create logging file handler
    file_handler = logging.FileHandler('shop.log', 'a')
    file_handler.setLevel(logger_level)

    # create logging console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger_level)

    #Set logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    vc = self.VoiceCommand()
    vc.set_command(self.process_command)

    while 1:
        prox_distance = check_proximity()
        if prox_distance < OCCUPIED_DISTANCE:
            if state == STATE_UNOCCUPIED:
                say("greet.mp3")
                state = STATE_OCCUPIED
                logger.info("Workshop Occupied")
            unoccupied_start = datetime.datetime.now()

        if prox_distance > OCCUPIED_DISTANCE:
            if (time.time() - unoccupied_start) > UNOCCUPIED_DURATION:
                say("goodbye.mp3")
                state = STATE_UNOCCUPIED
                logger.info("Workshop Unoccupied")

    GPIO.cleanup()


'''Voice Commands
    # Information Commands
    Datetime - Gives the Date and Time as audio
    Status - Provides memory, disk, processor and network information
    Project Report - Reports project name, number of images, videos and audio files in the current project

    #Media-centric
    Snap Webcam - Takes a picture with the webcam
    Snap Picam - Takes a picture with the Picam
    Roll Webcam - Captures a video with webcam
    Cut Webcam - Stops video capture from webcam
    Roll Picam - Captures a video with picam
    Cut Picam - Stops video capture from picam
    Record audio xx - Record xx seconds of audio

    Turn on light X - Turns on the specified light
    Turn off light X - Turns off the specified light
'''
