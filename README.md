# VideoCutter
Video Cutter and Compressing GUI tool/CLI


This is a simple video cutter GUI application that uses ffmpeg to cut videos.
Mainly, this is to get file sizes down to be sent over Discord.

## Functionality
The user can specify the following, 
- input video file
- output directory
- start time
- end time
- video quality / zip functionlity
 
This script only has one dependency (provided python is installed)
`pip install tk`
All contents within tools directory requires unzipping

Further downloads are needed for ffmpeg (video cutting) and ffprobe (obtaining video duration)
these are available from https://ffmpeg.org/download.html
Download these if needed, and place them in a 'tools' directory in the same directory as this script.

Your directory should look like this:
```
 ├── buffmpeg.py
 ├── tools
 │   ├── ffmpeg.exe
 │   └── ffprobe.exe

```
