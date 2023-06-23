import argparse

import cv2
import numpy as np
import win32con
import win32gui

from iterate import iterate_and_find
from screenshot import get_hwnd, screenshot

parser = argparse.ArgumentParser()
parser.add_argument("window_name", type=str, help="A string argument")
args = parser.parse_args()

MIRROR_WIN_NAME = "Mirror"
DELAY_MIRRORING = 250
DELAY_NOTHING = 1000
# create a window to display the mirror image
cv2.namedWindow(MIRROR_WIN_NAME, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(MIRROR_WIN_NAME, cv2.WND_PROP_TOPMOST, 1)
hwnd = get_hwnd(args.window_name)
mirror_hwnd = get_hwnd(MIRROR_WIN_NAME)
x = y = w = h = None
prev_shot = None
# loop over the frames
while True:
    # capture a screenshot of the screen
    shot = screenshot(hwnd)
    if shot is None:
        print(
            "Can't find the window. Check if the name is correct or try "
            "running as admin."
        )
        cv2.waitKey(DELAY_NOTHING)

    elif shot == "focused":
        print("The window is focused.")

        if type(prev_shot).__name__ == "Image":
            win32gui.SendMessage(
                mirror_hwnd, win32con.WM_SYSCOMMAND, win32con.SC_MINIMIZE, 0
            )

        cv2.waitKey(DELAY_NOTHING)

    elif shot == "not enough image data":
        print(f"Looking through all the windows that contain '{args.window_name}'")
        hwnd = iterate_and_find(args.window_name)
        cv2.waitKey(DELAY_NOTHING)

    else:
        # convert the screenshot to a NumPy array
        screenshot_array = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)

        if prev_shot == "focused":
            win32gui.SendMessage(
                mirror_hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0
            )

        # display the mirror image in the window
        cv2.imshow(MIRROR_WIN_NAME, screenshot_array)

        # wait for a key press to exit the program
        if cv2.waitKey(DELAY_MIRRORING) == ord("q"):
            break
    prev_shot = shot
# release the window and exit the program
cv2.destroyAllWindows()
