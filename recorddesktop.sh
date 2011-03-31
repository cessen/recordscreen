#!/bin/sh

# Call like this:
# recorddesktop.sh [optional_output_path.avi]
# Hit 'q' to stop.

# FPS to record at
FPS=15

# Number of pixels to crop off the desktop
CROP_TOP=0
CROP_BOTTOM=0
CROP_LEFT=0
CROP_RIGHT=0

# Output file path.  Default if none is given.
OUTNAME=$1
if [ "$OUTNAME" = "" ]
then
    OUTNAME=out_`date +%s`.mkv
fi

# Path to record temp files
TMPNAME=/tmp/out_`date +%s`

# Get desktop resolution
D=`xdpyinfo | grep dimensions | sed -e 's/.*dimensions:[ ]*//g' | sed -e 's/[ ]*pixels.*//g'`
W=`echo $D | sed -e 's/x.*//g'`
H=`echo $D | sed -e 's/.*x//g'`

# Calculate cropping
W=`expr $W "-" $CROP_LEFT`
W=`expr $W "-" $CROP_RIGHT`
H=`expr $H "-" $CROP_TOP`
H=`expr $H "-" $CROP_BOTTOM`
W_OFFSET=$CROP_LEFT
H_OFFSET=$CROP_TOP

# h264 only accepts resolutions in multiples of 2
# so make sure the recording dimensions are even.
W2=`expr $W "/" 2`
W2=`expr $W2 "*" 2`
H2=`expr $H "/" 2`
H2=`expr $H2 "*" 2`
D="$W2"x"$H2"

# Record audio and video to temp files.
ffmpeg -f x11grab -r $FPS -s $D -i :0.0+$W_OFFSET,$H_OFFSET -sameq -vcodec libx264 -vpre lossless_ultrafast -threads 2 $TMPNAME.avi &
V_ID=$!
ffmpeg -f alsa -ac 2 -i pulse -b 192k -threads 1 -acodec pcm_s16le $TMPNAME.wav
kill $V_ID
sleep 1s

# Mux audio and video temp files into final output file.
ffmpeg -i $TMPNAME.avi -i $TMPNAME.wav -vcodec copy -acodec copy $OUTNAME

# Remove temp files.
rm $TMPNAME.avi $TMPNAME.wav

# Done!
echo "Done recording."

