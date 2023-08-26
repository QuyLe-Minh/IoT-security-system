from Adafruit_IO import Client,Feed,Data
import sys
# from threading import *



topic_send = "to-esp8266"
AIO_USERNAME='quandinh10'
AIO_KEY='aio_zGuF35Mldcl20zVSQFWG9fOzGt8Q'
detect = "detect_signal"
FEED_ID =  [detect]


def connected(client):
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID))
    for id in FEED_ID:
        client.subscribe(id)

def subscribe(client, userdata, mid, granted_qos):
    print('Subscribed to {0} with QoS {1}'.format(mid, granted_qos[0]))

# check_sync = Semaphore(1)
# check = False
def message(client, feed_id, payload):
    # check_sync.acquire()
    # global check
    # check = True
    print('Feed {0} received new value: {1}'.format(feed_id, payload))
    # check_sync.release()
        
def disconnected(client):
    print('Disconnected from Adafruit IO!')
    sys.exit(1)