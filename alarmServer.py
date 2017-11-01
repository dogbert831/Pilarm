import RPi.GPIO as GPIO 
import os
import ConfigParser 
import time 
import requests 
import logging 
import threading 

GPIO.setmode(GPIO.BOARD)
GPIO.setup (7, GPIO.OUT) #LED on pin 7
GPIO.setup (7, GPIO.LOW)

#Open configuration file
config = ConfigParser.ConfigParser()
script_dir = os.path.dirname(__file__) 
config.read(os.path.join(script_dir, 'PilarmServer.conf'))

#Get Pilarm settings and configure logging
gpio_zones = list(map(int, config.get('Pilarm', 'gpio_zones').split(',')))
print gpio_zones
log_file = config.get('Pilarm', 'log_file') 
logging.basicConfig(filename=log_file, filemode='a', format="%(asctime)s %(levelname)s %(message)s", datefmt="%m-%d-%y %H:%M:%S", level=logging.INFO) 
logging.getLogger("urllib3").setLevel(logging.WARNING)

#Handler for GPIO events
def gpio_handler(zone):
    try:
        GPIO.output(7, GPIO.HIGH)
        message = 'Zone ' + str(zone) + ' ' + ('opened' if GPIO.input(zone) else 'closed')
        print message
        logging.info(message)
    except Exception as e:
        logging.exception("Error processing GPIO event: " + str(e))

#Return JSON string for single zone (single option used if output will be combined with additional zones)
def get_zone_json(zone, single = True):
    json = '"' + str(zone) + '":"' + str(GPIO.input(zone)) + '"'
    if single:
        json = '{' + json + '}'
    return json

#Return JSON string for all zones
def get_all_zones_json():
    json = '{'
    for zone in gpio_zones:
        json = json + get_zone_json(zone, False)
        if zone == gpio_zones[-1]:
            json = json + '}'
        else:
            json = json + ','
    return json

#Begin Pilarm
logging.info('Initializing Pilarm')

for zone in gpio_zones:
    print zone
    GPIO.setup(zone, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(zone, GPIO.FALLING, gpio_handler, bouncetime=200) 
logging.info('Beginning Pilarm loop')

while True:
    try:
        data=get_all_zones_json()
        print data
        time.sleep(5)
    except Exception as e:
        logging.exception("Error in alarm loop: " + str(e))

#Stop Pilarm    
logging.info('Exited Pilarm loop and shutting down')

#Close down GPIO registrations
GPIO.cleanup()
