#!/bin/sh

# Call like this:
# recordwindow.sh [optional_output_path.avi]
# Then click on the window you want to record.
# Hit 'q' to stop.

# FPS to record at
FPS=15  

# Output file path.  Default if none is given.
OUTNAME=$1
if [ "$OUTNAME" = "" ]
then
    OUTNAME=out_`date +%s`.mkv
fi

# Path to record temp files
TMPNAME=/tmp/out_`date +%s`

# Get window info
WININFO=`xwininfo`
X=`echo "$WININFO" | grep 'Absolute upper-left X:' | sed -e 's/[^[0-9]//g'`
Y=`echo "$WININFO" | grep 'Absolute upper-left Y:' | sed -e 's/[^[0-9]//g'`
W=`echo "$WININFO" | grep 'Width:' | sed -e 's/[^[0-9]//g'`
H=`echo "$WININFO" | grep 'Height:' | sed -e 's/[^[0-9]//g'`

# h264 only accepts resolutions in multiples of 2
# so make the recording dimensions even.
W2=`expr $W "/" 2`
W2=`expr $W2 "*" 2`
H2=`expr $H "/" 2`
H2=`expr $H2 "*" 2`
D="$W2"x"$H2"

# Record audio and video to temp files.
ffmpeg -f x11grab -r $FPS -s $D -i :0.0+$X,$Y -sameq -vcodec libx264 -vpre lossless_ultrafast -threads 2 $TMPNAME.avi &
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

