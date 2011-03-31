#!/usr/bin/env python

import os
import os.path
import glob
import time
import random
import sys
import tempfile
import optparse
import subprocess
import re

# Optional packages
have_tk = False
try:
    import Tkinter
    have_tk = True
except ImportError:
    pass

have_multiproc = False
try:
    import multiprocessing
    have_multiproc = True
except ImportError:
    pass


def get_desktop_resolution():
    """ Returns the resolution of the desktop as a tuple.
    """
    if have_tk:
        # Use tk to get the desktop resolution if we have it
        root = Tkinter.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return (width, height)
    else:
        # Otherwise call xdpyinfo and parse its output
        try:
            proc = subprocess.Popen("xdpyinfo", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except OSError:
            return None
        out, err = proc.communicate()
        lines = out.split("\n")
        for line in lines:
            if "dimensions" in line:
                line = re.sub(".*dimensions:[ ]*", "", line)
                line = re.sub("[ ]*pixels.*", "", line)
                wh = line.strip().split("x")
                return (int(wh[0]), int(wh[1]))


def video_capture_line(fps, x, y, height, width, output_path):
    """ Returns the command line to capture video, in a list form
        compatible with Popen.
    """
    threads = 2
    if have_multiproc:
        # Detect the number of threads we have available
        threads = multiprocessing.cpu_count()

    return ["ffmpeg",
            "-f", "x11grab",
            "-r", str(fps),
            "-s", "%dx%d" % (int(height), int(width)),
            "-i", ":0.0+%d,%d" % (int(x), int(y)),
            "-sameq",
            "-vcodec", "libx264",
            "-vpre", "lossless_ultrafast",
            "-threads", str(threads),
            str(output_path)]


def audio_capture_line(output_path):
    """ Returns the command line to capture audio, in a list form
        compatible with Popen.
    """
    return ["ffmpeg",
            "-f", "alsa",
            "-ac", "2",
            "-i", "pulse",
            "-b", "192k",
            "-threads", "1",
            str(output_path)]


def mux_line(video_path, audio_path, output_path):
    """ Returns the command line to mux audio and video, in a list form
        compatible with Popen.
    """
    return ["ffmpeg",
            "-i", str(video_path),
            "-i", str(audio_path),
            "-vcodec", "copy",
            "-acodec", "copy",
            str(output_path)]


def random_id(length = 8):
    """ Generates a random alphanumeric id string.
    """
    tlength = int(length / 2)
    rlength = int(length / 2) + int(length % 2)

    chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    text = ""
    for i in range(0, rlength):
        text += random.choice(chars)
    text += str(hex(int(time.time())))[2:][-tlength:].rjust(tlength, '0')[::-1]
    return text


def get_default_output_path():
    """ Creates a default output file path.
        Pattern: out_####.avi
    """
    filenames = glob.glob("out_????.avi")
    for i in range(1, 9999):
        name = "out_" + str(i).rjust(4,'0') + ".avi"
        tally = 0
        for f in filenames:
            if f == name:
                tally += 1
        if tally == 0:
            return name
    return "out_9999.avi"


if __name__ == "__main__":
    # Set up default file paths
    tmp_path = tempfile.gettempdir() + "/" + tempfile.gettempprefix() + "_" + random_id()
    tmp_vpath = os.path.normpath(tmp_path + ".avi")
    tmp_apath = os.path.normpath(tmp_path + ".wav")
    out_path = get_default_output_path()

    # Parse command line arguments
    #parser = optparse.OptionParser(usage=USAGE_MESSAGE)
    parser = optparse.OptionParser(usage="%prog [options] [output_file.avi]")
    parser.add_option("-w", "--use-window", action="store_true", dest="use_window",
                      default=False,
                      help="select a window to record")
    parser.add_option("-r", "--fps", dest="fps",
                      type="int", default=15,
                      help="frame rate to capture video at")
    parser.add_option("-p", "--position", dest="xy", metavar="XxY",
                      type="string", default=None,
                      help="upper left corner of the capture area in pixels from the upper left of the screen (e.g. 50x64)")
    parser.add_option("-s", "--size", dest="size",
                      type="string", default=None, metavar="WIDTHxHEIGHT",
                      help="resolution of the capture area in pixels (e.g. 1280x720)")
    parser.add_option("--crop-top", dest="crop_top",
                      type="int", default=0,
                      help="number of pixels to crop off the top of the capture area")
    parser.add_option("--crop-bottom", dest="crop_bottom",
                      type="int", default=0,
                      help="number of pixels to crop off the bottom of the capture area")
    parser.add_option("--crop-left", dest="crop_left",
                      type="int", default=0,
                      help="number of pixels to crop off the left of the capture area")
    parser.add_option("--crop-right", dest="crop_right",
                      type="int", default=0,
                      help="number of pixels to crop off the right of the capture area")
    opts, args = parser.parse_args()

    # Output file path
    if len(args) >= 1:
        out_path = args[0]
        if not out_path.endswith(".avi") and \
           not out_path.endswith(".mov") and \
           not out_path.endswith(".mkv") and \
           not out_path.endswith(".ogv"):
            out_path += ".avi"

    # Get desktop resolution
    try:
        dres = get_desktop_resolution()
    except:
        print "Error: unable to determine desktop resolution."
        raise

    # Default capture values
    fps = opts.fps

    if opts.xy:
        xy = opts.xy.split("x")
        x = int(xy[0])
        y = int(xy[1])
    else:
        x = 0
        y = 0

    if opts.size:
        size = opts.size.split("x")
        width = int(size[0])
        height = int(size[1])
    else:
        width = dres[0]
        height = dres[1]


    # Calculate cropping
    width -= opts.crop_left + opts.crop_right
    height -= opts.crop_top + opts.crop_bottom
    x += opts.crop_left
    y += opts.crop_top

    # Capture audio and video to temporary files
    with open(os.devnull, 'w') as devnull:
        a = subprocess.Popen(audio_capture_line(tmp_apath), stdout=devnull, stdin=devnull, stderr=devnull)
        v = subprocess.Popen(video_capture_line(fps, x, y, width, height, tmp_vpath)).wait()
        a.terminate()

    # Mux audio and video into final output file
    print "Starting muxing..."
    time.sleep(1)
    m = subprocess.Popen(mux_line(tmp_vpath, tmp_apath, out_path)).wait()

    # Remove temporary files
    os.remove(tmp_vpath)
    os.remove(tmp_apath)

