import argparse

import cv2
import numpy as np

from iterate import iterate_and_find
from screenshot import get_hwnd, screenshot

parser = argparse.ArgumentParser()
parser.add_argument("window_name", type=str, help="A string argument")
args = parser.parse_args()

# create a window to display the mirror image
cv2.namedWindow("Mirror", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Mirror", cv2.WND_PROP_TOPMOST, 1)

hwnd = get_hwnd(args.window_name)
x = y = w = h = None
prev_shot = None
# loop over the frames
while True:
    # time.sleep(1)
    # capture a screenshot of the screen
    shot = screenshot(hwnd)
    if shot is None:
        print(
            "Can't find the window. Check if the name is correct or try "
            "running as admin."
        )
        cv2.waitKey(1000)

    elif shot == "focused":
        print("The window is focused.")
        if type(prev_shot).__name__ == "Image":
            x, y, w, h = cv2.getWindowImageRect("Mirror")
            cv2.destroyAllWindows()

        cv2.waitKey(1000)

    elif shot == "not enough image data":
        print(f"Looking through all the windows that contain '{args.window_name}'")
        hwnd = iterate_and_find(args.window_name)
        cv2.waitKey(1000)

    else:
        # convert the screenshot to a NumPy array
        # print(f"shot is: ||{shot}|| {type(shot)}")
        screenshot_array = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
        # screenshot_array = cv2.cvtColor(np.array(shot))

        if prev_shot == "focused":
            cv2.namedWindow("Mirror", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("Mirror", cv2.WND_PROP_TOPMOST, 1)
            cv2.moveWindow("Mirror", x, y)
            cv2.resizeWindow("Mirror", w, h)

        # display the mirror image in the window
        cv2.imshow("Mirror", screenshot_array)

        # wait for a key press to exit the program
        if cv2.waitKey(250) == ord("q"):
            break
    prev_shot = shot
# release the window and exit the program
cv2.destroyAllWindows()
