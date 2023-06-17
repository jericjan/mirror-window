import cv2
import numpy as np

from screenshot import screenshot
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('window_name', type=str, help='A string argument')
args = parser.parse_args()


# create a window to display the mirror image
cv2.namedWindow("Mirror", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Mirror", cv2.WND_PROP_TOPMOST, 1)
# loop over the frames
while True:
    # capture a screenshot of the screen
    shot = screenshot(args.window_name)
    if shot is None:
        print(
            "Can't find the window. Check if the name is correct or try running as admin."
        )
        break
    # convert the screenshot to a NumPy array
    screenshot_array = cv2.cvtColor(np.array(shot), cv2.COLOR_RGB2BGR)
    # screenshot_array = cv2.cvtColor(np.array(shot))

    # display the mirror image in the window
    cv2.imshow("Mirror", screenshot_array)

    # wait for a key press to exit the program
    if cv2.waitKey(1) == ord("q"):
        break

# release the window and exit the program
cv2.destroyAllWindows()
