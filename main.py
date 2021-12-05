import obspython as obs
import time
from PIL import Image
import png
import numpy
before = time.time()
name = "countdown"
paused = True
mins = 10
secs = 0
res = ''
img = ''
nixieImages = {}


def initImages():
    global nixieImages
    global res
    try:
        nixieImages = {c: Image.open("{}\\{}.png".format(res, c)) for c in ".0123456789"}
        nixieImages[':'] = Image.open("{}\\semicolon.png".format(res))
    except:
        obs.script_log(obs.LOG_ERROR, "Failed to load resources")

def craftGif(f, fps):
    cntdwn = mins*60+secs
    step = 1/fps
    imgs = []
    log = open("{}\\log".format(res), 'w')
    while True:
        if cntdwn > 0:
            s = str(int(cntdwn // 60)).zfill(2) + ":" + str(int(cntdwn) % 60).zfill(2) + "." + str(int(cntdwn * 1000) % 1000).zfill(3)
        else:
            s = "00:00.000"

        log.write("{}\n".format(s))
        resImage = Image.new("RGBA", (149*len(s), 422), (255, 0, 0, 0))
        for i in range(len(s)):
            resImage.paste(nixieImages[s[i]], (149*i, 0), nixieImages[s[i]])
        imgs.append(resImage)
        if cntdwn > 0:
            cntdwn -= step
        else:
            break
    log.close()
    imgs[0].save(f, save_all=True, transparency=0, append_images=imgs[1:], loop=0, duration=step*1000)

def craftImage(s, f):
    locnow = time.time()
    resImage = Image.new("RGBA", (149*len(s), 422), (255, 0, 0, 0))
    for i in range(len(s)):
        resImage.paste(nixieImages[s[i]], (149*i, 0), nixieImages[s[i]])
    resImage.save(f, compress_level=0, compress_type=1)
    obs.script_log(obs.LOG_DEBUG, "{} elapsed".format(time.time()-locnow))
    #w = png.Writer(149*len(s), 422, compression=0)
    #r = open(f, 'wb')
    #obs.script_log(obs.LOG_DEBUG, "{}".format(type(numpy.array(resImage))))
    #w.write(r, numpy.array(resImage))
    #r.close()

def set_countdown(props, prop):
    source = obs.obs_get_source_by_name(name)
    if not source:
        obs.script_log(obs.LOG_ERROR, "BRUH NIGGA")
        return
    settings = obs.obs_data_create()
    s = str(mins).zfill(2) + ":" + str(secs).zfill(2) + "." + str().zfill(3)

    craftImage(s, img)
    obs.obs_data_set_string(settings, "path", img)
    obs.obs_source_update(source, settings)
    obs.obs_data_release(settings)
    obs.obs_source_release(source)
    global paused
    paused = True


def paused_button(props, prop):
    global paused
    if paused:
        global before
        before = time.time()
        paused = False
    else:
        paused = True

def script_tick(nigger):
    global paused
    if paused:
        return
    source = obs.obs_get_source_by_name(name)
    if not source:
        obs.script_log(obs.LOG_ERROR, "BRUH NIGGA")
        return
    now = time.time()
    settings = obs.obs_data_create()
    cntdwn = (before + offset) - now
    if cntdwn < 0:
        s = "00:00.000"
        
        paused = True
    else:
        s = str(int(cntdwn // 60)).zfill(2) + ":" + str(int(cntdwn) % 60).zfill(2) + "." + str(int(cntdwn * 1000) % 1000).zfill(3)
    craftImage(s, img)
    obs.obs_data_set_string(settings, "path", img)
    obs.obs_source_update(source, settings)
    obs.obs_data_release(settings)
    obs.obs_source_release(source)




def script_description():
    return "Countdown with milliseconds"

def script_update(settings):
    global paused
    global offset
    global mins
    global secs
    global before
    global name
    global res
    global img
    paused = True
    mins = obs.obs_data_get_int(settings, "minutes")
    secs = obs.obs_data_get_int(settings, "seconds")
    name = obs.obs_data_get_string(settings, "name")
    res = obs.obs_data_get_string(settings, "res")
    img = obs.obs_data_get_string(settings, "img")
    initImages()
    offset = mins*60+secs
    before = time.time()

def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "minutes", 10)
    obs.obs_data_set_default_int(settings, "seconds", 0)
    obs.obs_data_set_default_string(settings, "name", "countdown")

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_int(props, "minutes", "Countdown minutes", 0, 600, 1)
    obs.obs_properties_add_int(props, "seconds", "Countdown seconds", 0, 59, 1)
    obs.obs_properties_add_text(props, "name", "Image name", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_path(props, "res", "Resources folder", obs.OBS_PATH_DIRECTORY, '', '')
    obs.obs_properties_add_button(props, "pause", "Pause and reset countdown", paused_button)
    obs.obs_properties_add_path(props, "img", "Image path", obs.OBS_PATH_FILE, '', '')
    obs.obs_properties_add_button(props, "set", "Set countdown", set_countdown)
    return props
