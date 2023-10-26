import argparse
from tkinter import Label, Menu, Tk, Toplevel, Listbox, Button, END, simpledialog

import numpy as np
from PIL import Image, ImageTk

from iterate import iterate_and_find
from screenshot import get_hwnd, screenshot
from classes import JSONHandler

parser = argparse.ArgumentParser()
parser.add_argument("window_name", type=str, help="A string argument")
parser.add_argument("--disable-auto-popup", action="store_true")
parser.add_argument("--disable-minimize", action="store_true")
args = parser.parse_args()

print(f"Disable auto popup: {args.disable_auto_popup}")
print(f"Disable auto popup: {args.disable_minimize}")

DO_MINIMIZE = not args.disable_minimize
DO_POPUP = not args.disable_auto_popup


MIRROR_WIN_NAME = f"Mirror - [{args.window_name}]"
DELAY_MIRRORING = 250
DELAY_NOTHING = 1000

json_handler = JSONHandler("settings.json")

window = Tk()  # Makes main window
window.wm_title(MIRROR_WIN_NAME)  # TODO: add resizable
window.geometry("50x50")
window.attributes("-topmost", True)

lmain = Label(window)
lmain.pack()

hwnd = get_hwnd(args.window_name)
x = y = w = h = None
prev_shot = None


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
            print("POPPING UP ")
            window.deiconify()

        img = Image.fromarray(np.array(shot))
        img.thumbnail((window.winfo_width(), window.winfo_height()))

        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)

        lmain.after(DELAY_MIRRORING, show_frame)

    prev_shot = shot


def toggle_autopopup(menu):
    global DO_POPUP
    DO_POPUP = not DO_POPUP    
    menu.entryconfigure(1, label=f"Enable auto-popup: {DO_POPUP}")


def toggle_minimize(menu):
    global DO_MINIMIZE
    DO_MINIMIZE = not DO_MINIMIZE    
    menu.entryconfigure(2, label=f"Enable auto-minimize: {DO_MINIMIZE}")



def switch_window():
    # TODO: create json
    # TODO: add popup for input of new stuff
    window.attributes("-topmost", False)

    def add_item(listbox):
        # Prompt the user for input
        new_item = simpledialog.askstring("Add Item", "Enter a window name:")

        # Add the new item to the Listbox
        if new_item:
            listbox.insert(END, new_item)

        json_handler.add(new_item)

    popup = Toplevel(window)
    popup.title("Popup Window")

    # Create a Listbox widget
    listbox = Listbox(popup)
    listbox.pack()

    # Add items to the Listbox
    dic = json_handler.read()
    window_names = dic[json_handler.key]    
    for item in window_names:
        listbox.insert(END, item)

    # Create the "Use" button
    use_button = Button(popup, text="Use")
    use_button.pack()

    # Create the "Add" button
    add_button = Button(popup, text="Add", command=lambda: add_item(listbox))
    add_button.pack()

    remove_button = Button(popup, text="Remove")
    remove_button.pack()

    window.attributes("-topmost", True)

menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Switch window", command=switch_window)  # command=func_Here
filemenu.add_command(label=f"Enable auto-popup: {DO_POPUP}", command=lambda: toggle_autopopup(filemenu))
filemenu.add_command(label=f"Enable auto-minimize: {DO_MINIMIZE}", command=lambda: toggle_minimize(filemenu))
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="Settings", menu=filemenu)

show_frame()
window.config(menu=menubar)
window.mainloop()
