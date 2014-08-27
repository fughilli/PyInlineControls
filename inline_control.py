import win32api as win
import pyaudio
import sys
import struct
import time

DEBUG = 0

def debugPrint( debugValue ):
    if(DEBUG != 0):
        print debugValue

# +-----------------------------------------+
# | virtual key mapping and media functions |
# +-----------------------------------------+
VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1

VK_VOLUME_UP = 0xAF
VK_VOLUME_DN = 0xAE

MEDIA_PLAY_PAUSE_KEYCODE = win.MapVirtualKey(VK_MEDIA_PLAY_PAUSE, 0)
MEDIA_NEXT_TRACK_KEYCODE = win.MapVirtualKey(VK_MEDIA_NEXT_TRACK, 0)
MEDIA_PREV_TRACK_KEYCODE = win.MapVirtualKey(VK_MEDIA_PREV_TRACK, 0)

VOLUME_UP_KEYCODE = win.MapVirtualKey(VK_VOLUME_UP, 0)
VOLUME_DN_KEYCODE = win.MapVirtualKey(VK_VOLUME_DN, 0)

# play/pause the currently playing media
def playPause():
    debugPrint( "play/pause media" )
    win.keybd_event(VK_MEDIA_PLAY_PAUSE, MEDIA_PLAY_PAUSE_KEYCODE)

# jump to the next track in the media queue
def nextTrack():
    debugPrint( "next track" )
    win.keybd_event(VK_MEDIA_NEXT_TRACK, MEDIA_NEXT_TRACK_KEYCODE)

# jump to the last track in the media queue
def prevTrack():
    debugPrint( "previous track" )
    win.keybd_event(VK_MEDIA_PREV_TRACK, MEDIA_PREV_TRACK_KEYCODE)

# increase volume
def volumeUp():
    debugPrint( "volume up" )
    win.keybd_event(VK_VOLUME_UP, VOLUME_UP_KEYCODE)

# decrease volume
def volumeDn():
    debugPrint( "volume down" )
    win.keybd_event(VK_VOLUME_DN, VOLUME_DN_KEYCODE)

# +------------------+
# | Click processing |
# +------------------+
CLICK_DOWN = 0
CLICK_UP = 1

CLICK_SPACING_THRESHOLD = 0.4
CLICK_EVENT_FIRE_DELAY = 0.5

click_start_time_g = 0
click_duration_g = 0
click_spacing_g = 0
click_count_g = 0
click_last_release_time_g = 0
new_event_g = False

VOLUME_LOCK_UNLOCKED = 0
VOLUME_LOCK_UP = 1
VOLUME_LOCK_DOWN = 2

volume_direction_lock = VOLUME_LOCK_UNLOCKED

def volumeUpLockToggle():
    global volume_direction_lock
    if(volume_direction_lock != VOLUME_LOCK_UP):
        volume_direction_lock = VOLUME_LOCK_UP
    else:
        volume_direction_lock = VOLUME_LOCK_UNLOCKED

def volumeDnLockToggle():
    global volume_direction_lock
    if(volume_direction_lock != VOLUME_LOCK_DOWN):
        volume_direction_lock = VOLUME_LOCK_DOWN
    else:
        volume_direction_lock = VOLUME_LOCK_UNLOCKED

def volumeLockUnlock():
    global volume_direction_lock
    volume_direction_lock = VOLUME_LOCK_UNLOCKED

def singleClickDelegate():
    global volume_direction_lock
    opts = {
        VOLUME_LOCK_UNLOCKED : playPause,
        VOLUME_LOCK_UP : volumeUp,
        VOLUME_LOCK_DOWN : volumeDn
        }
    try:
        opts[volume_direction_lock]()
    except KeyError:
        pass
        

def multiClick( click_count ):
    debugPrint( "Num clicks: %d" % click_count )
    opts = {
        1 : singleClickDelegate,
        2 : nextTrack,
        3 : prevTrack,
        4 : volumeUpLockToggle,
        5 : volumeDnLockToggle,
        6 : volumeLockUnlock
        }
    try:
        opts[click_count]()
    except KeyError:
        pass
    

def clickOccurred( click_type ):
    global click_last_release_time_g
    global click_start_time_g
    global click_duration_g
    global click_spacing_g
    global click_count_g
    global new_event_g
    
    if(click_type == CLICK_DOWN):
        click_spacing_g = (time.clock() - click_start_time_g)
        click_start_time_g = time.clock()
        debugPrint( "click press" )

        if(click_spacing_g > CLICK_SPACING_THRESHOLD):
            click_count_g = 0
            
    if(click_type == CLICK_UP):
        click_duration_g = (time.clock() - click_start_time_g)
        debugPrint( "click release %f" % click_duration_g )
        click_start_time = click_last_release_time_g = time.clock()
        new_event_g = True

        click_count_g = click_count_g + 1

def updateClickEngine():
    global click_last_release_time_g
    global click_count_g
    global new_event_g

    if( new_event_g and (time.clock() - click_last_release_time_g) > CLICK_EVENT_FIRE_DELAY ):
        new_event_g = False
        multiClick( click_count_g )

# +--------------------+
# | audio stream setup |
# +--------------------+
chunk = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
THRESHOLD = 15000
RISING_EDGE = 0
FALLING_EDGE = 1

edge_to_detect = RISING_EDGE

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS, 
                rate=RATE, 
                input=True,
                output=True,
                frames_per_buffer=chunk,
                input_device_index=0)

while(1):
    # initialize an array to store the unpacked integer samples
    unpackedData = []

    data = []

    # read a chunk of samples
    try:
        data = stream.read(chunk)
    except IOError as e:
        debugPrint( "IOError; audio device probably disconnected. Waiting two second..." )
        time.sleep(2)
        debugPrint( "Retrying..." )
        stream = p.open(format=FORMAT,
                channels=CHANNELS, 
                rate=RATE, 
                input=True,
                output=True,
                frames_per_buffer=chunk)
        continue
    
    # unpack the samples to unpackedData
    for j in range(0, chunk):
        unpackedData.append(struct.unpack_from("<h", data, j * 2)[0])

    average = 0

    for i in range(0, chunk):
        average += unpackedData[i]

    average = (average / len(unpackedData))
    
    if( average > THRESHOLD and edge_to_detect == RISING_EDGE):
        edge_to_detect = FALLING_EDGE
        clickOccurred(CLICK_DOWN)
    if( average < -THRESHOLD and edge_to_detect == FALLING_EDGE):
        edge_to_detect = RISING_EDGE
        clickOccurred(CLICK_UP)

    updateClickEngine()


