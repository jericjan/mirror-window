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

        # display the mirror image in the window
        cv2.imshow("Mirror", screenshot_array)

        # wait for a key press to exit the program
        if cv2.waitKey(250) == ord("q"):
            break

# release the window and exit the program
cv2.destroyAllWindows()
