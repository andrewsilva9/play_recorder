# Play Recorder
Forked from a repo called atbswp. Currently being built for Windows.

# Install instructions

Windows
```shell
git clone https://github.com/andrewsilva9/play_recorder
cd play_recorder/
pip install wxPython pyautogui pynput pywin32 opencv-python numpy mss
python play_recorder/main.py
```
# What does this do?
The purpose of this tool is to record all input (mouse/keyboard input) to your PC as well as video of your gameplay.
After recording, input data is saved in a file in the format: `{timestamp} | {command_name} | {command_args}` (for example, `1688920152.148975 | moveTo | 3360, 428`).
Video data is saved in a 512x288 video at roughly 10 fps (at least, in my current setup).
Because video frames don't come with timestamps to align them to your input, I also save a "video_timestamps.txt" file, which has timestamps for every frame of the video.

# Usage

Run the `main.py` script inside of the `play_recorder` directory.
```shell
cd play_recorder
python main.py
```
And then go to the settings and type the name of the window that you want to record. 
All open windows will auto-populate the text-box in a comma-separated list, so you should be able to just find the window for your game and then delete all other windows from that text-box and hit OK.

Feel free to tune the mouse-sensitivity settings as well. 

When ready, hit the "Record" button.
Python will automatically start recording all mouse movements, clicks, key presses, and images from your game.

When you've finished, hit the "Save" button and enter a name for your file. 
The input-recording will all be dumped into that file that you create, and the video and timestamps for the video frames will be dumped alongside.

**Warning**
Note that input-recording (mouse/keyboard recording) is _global_, it is not constrained actions taken within the game.
So, if you alt-tab out and search for something, your input recording will have all of that data recorded.