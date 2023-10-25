import argparse

import cv2
import numpy as np
import win32con
import win32gui

from iterate import iterate_and_find
from screenshot import get_hwnd, screenshot

import tkinter as tk


parser = argparse.ArgumentParser()
parser.add_argument("window_name", type=str, help="A string argument")
parser.add_argument('--disable-auto-popup', action='store_true')
parser.add_argument('--disable-minimize', action='store_true')
args = parser.parse_args()

print(f"Disable auto popup: {args.disable_auto_popup}")
print(f"Disable auto popup: {args.disable_minimize}")

DO_MINIMIZE = not args.disable_minimize
DO_POPUP = not args.disable_auto_popup

MIRROR_WIN_NAME = f"Mirror - [{args.window_name}]"
DELAY_MIRRORING = 250
DELAY_NOTHING = 1000


window = tk.Tk()  # Makes main window
window.wm_title(MIRROR_WIN_NAME)  # TODO: add resizable, add topmost

lmain = tk.Label(window)
lmain.pack()

hwnd = get_hwnd(args.window_name)
mirror_hwnd = get_hwnd(MIRROR_WIN_NAME)
x = y = w = h = None
prev_shot = None
# loop over the frames


def show_frame():
    global prev_shot
    global hwnd
    
    # capture a screenshot of the screen
    shot = screenshot(hwnd)
    if shot is None:
        print(
            "Can't find the window. Check if the name is correct or try "
            "running as admin."
        )        
        lmain.after(DELAY_NOTHING, show_frame)

    elif shot == "focused":
        print("The window is focused.")

        if type(prev_shot).__name__ == "Image" and DO_MINIMIZE:
            win32gui.SendMessage(
                mirror_hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0
            )

        lmain.after(DELAY_NOTHING, show_frame)

    elif shot == "not enough image data":
        print(f"Looking through all the windows that contain '{args.window_name}'")
        hwnd = iterate_and_find(args.window_name)
        lmain.after(DELAY_NOTHING, show_frame)

    else:
        # convert the screenshot to a NumPy array
        screenshot_array = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)

        if prev_shot == "focused" and (DO_POPUP or not DO_MINIMIZE):            
            win32gui.SendMessage(
                mirror_hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0
            )

        # display the mirror image in the window
        cv2.imshow(MIRROR_WIN_NAME, screenshot_array)

        lmain.after(DELAY_MIRRORING, show_frame)  # TODO: key press Q check

    prev_shot = shot


show_frame()
window.mainloop()

