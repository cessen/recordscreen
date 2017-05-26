# RecordScreen.py

RecordScreen.py is a simple command-line front end to recording screencasts with [ffmpeg](http://ffmpeg.org) or [avconv from libav](https://libav.org).  The ffmpeg and avconv command-line options for this are a bit tricky, so this script aims to present a more convenient and pleasant command-line experience.

## Example Usage

To record your entire desktop to the file `output_file.mkv` with default settings, enter this at the command line:

```
recordscreen.py output_file.mkv
```

When you are finished recording, you can either press `q` or hit `Ctrl-C` to stop.  Note that if no output file is specified it will create a file in the current directory with the name `out_####.mkv`, where `####` is a number that is incremented to avoid overwriting any existing files.

By default, recordscreen.py records at 15fps.  You can change that with the `-r` flag.  For example, to record at 30fps:

```
recordscreen.py -r 30 output_file.mkv
```

Similarly, the default video and audio codecs are h.264 and aac, respectively.  To use something else, you can do this:

```
recordscreen.py --vcodec=vp8 --acodec=pcm output_file.mkv
```

You can save to a different container format simply by changing the file extension of the output file:

```
recordscreen.py output_file.mp4
```

The available containers are: `avi`, `mp4`, `mov`, `mkv`, `ogv`, and `webm`.

There are other options available as well, such as recording only part of the screen.  All options are documented in the help:

```
recordscreen.py --help
```
