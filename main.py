import argparse
from tkinter import Label, Menu, Tk

import numpy as np
from PIL import Image, ImageTk

from iterate import iterate_and_find
from screenshot import get_hwnd, screenshot

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


window = Tk()  # Makes main window
window.wm_title(MIRROR_WIN_NAME)  # TODO: add resizable
window.geometry("50x50")
window.attributes('-topmost', True)


lmain = Label(window)
lmain.pack()

hwnd = get_hwnd(args.window_name)
# mirror_hwnd = window.winfo_id()  # get_hwnd(MIRROR_WIN_NAME)
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
            print("MINIMIZING")
            window.iconify()

        lmain.after(DELAY_NOTHING, show_frame)

    elif shot == "not enough image data":
        print(f"Looking through all the windows that contain '{args.window_name}'")
        hwnd = iterate_and_find(args.window_name)
        lmain.after(DELAY_NOTHING, show_frame)

    else:

        if prev_shot == "focused" and (DO_POPUP or not DO_MINIMIZE):            
            print("POPPING UP ", mirror_hwnd)

            window.deiconify()

        img = Image.fromarray(np.array(shot))        
        img.thumbnail((window.winfo_width(), window.winfo_height())) 

        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)




        lmain.after(DELAY_MIRRORING, show_frame)

    prev_shot = shot


def toggle_autopopup():
    global DO_POPUP
    DO_POPUP = not DO_POPUP


def toggle_minimize():
    global DO_MINIMIZE
    DO_MINIMIZE = not DO_MINIMIZE


menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Switch window")  # command=func_Here
filemenu.add_command(label="Toggle auto-popup", command=toggle_autopopup)
filemenu.add_command(label="Toggle auto-minimize", command=toggle_minimize)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="Settings", menu=filemenu)

show_frame()
window.config(menu=menubar)
window.mainloop()

