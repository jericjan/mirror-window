import argparse
from tkinter import (
    Label,
    Menu,
    Tk,
    Toplevel,
    Listbox,
    Button,
    END,
    simpledialog,
    messagebox,
)

import numpy as np
from PIL import Image, ImageTk

from iterate import iterate_and_find
from screenshot import get_hwnd, screenshot
from classes import JSONHandler


parser = argparse.ArgumentParser()
parser.add_argument(
    "window_name", type=str, help="A string argument", default=None, nargs="?"
)
parser.add_argument(
    "--auto-popup", "-p", type=lambda x: x.lower(), choices=["true", "false"], nargs="?"
)

parser.add_argument(
    "--auto-minimize",
    "-m",
    type=lambda x: x.lower(),
    choices=["true", "false"],
    nargs="?",
)

args = parser.parse_args()

print(f"auto_popup: {args.auto_popup}")
print(f"auto_minimize: {args.auto_minimize}")

json_handler = JSONHandler("settings.json")

DO_MINIMIZE = (
    True
    if args.auto_minimize == "true"
    else False
    if args.auto_minimize == "false"
    else json_handler.get_current("auto_minimize")
)

DO_POPUP = (
    True
    if args.auto_popup == "true"
    else False
    if args.auto_popup == "false"
    else json_handler.get_current("auto_popup")
)

saved_current_win = json_handler.get_current("window")
WIN_NAME = (
    args.window_name
    if args.window_name is not None
    else saved_current_win
    if saved_current_win != ""
    else None
)

DELAY_MIRRORING = 250
DELAY_NOTHING = 1000


window = Tk()  # Makes main window


def update_title():
    window.wm_title(f"Mirror - [{WIN_NAME}]")


update_title()
window.geometry("500x500")
window.attributes("-topmost", True)

lmain = Label(window)
lmain.pack(anchor="center", expand=True)
status_text = Label(window)


x = y = w = h = None
prev_shot = None

HWND_CHANGED = True


def show_frame():

    global prev_shot
    global hwnd
    global HWND_CHANGED
    global status_text

    if prev_shot is None:
        status_text.pack_forget()

    if HWND_CHANGED:
        json_handler.set_current("window", WIN_NAME)
        hwnd = get_hwnd(WIN_NAME)
        HWND_CHANGED = False

    # capture a screenshot of the screen
    shot = screenshot(hwnd)
    if shot is None:
        print(
            "Can't find the window. Check if the name is correct or try "
            "running as admin."
        )
        
        lmain.imgtk = None
        status_text.configure(
            text="Can't find the window. Check if the name is correct or try "
            "running as admin."
        )
        status_text.pack(before=lmain)

        lmain.after(DELAY_NOTHING, show_frame)

    elif shot == "focused":
        # print("The window is focused.")

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
    json_handler.set_current("auto_popup", DO_POPUP)
    menu.entryconfigure(1, label=f"Enable auto-popup: {DO_POPUP}")


def toggle_minimize(menu):
    global DO_MINIMIZE
    DO_MINIMIZE = not DO_MINIMIZE
    json_handler.set_current("auto_minimize", DO_MINIMIZE)
    menu.entryconfigure(2, label=f"Enable auto-minimize: {DO_MINIMIZE}")


def switch_window():
    def add_item(listbox):
        # Prompt the user for input
        new_item = simpledialog.askstring(
            "Add Item", "Enter a window name:", parent=listbox
        )

        # Add the new item to the Listbox
        if new_item:
            listbox.insert(END, new_item)

        json_handler.add(new_item)

    def remove_item(listbox):
        selected_index = listbox.curselection()
        if selected_index:
            index = selected_index[0]
            item = listbox.get(index)
            print("Selected item:", item)
            json_handler.remove(index)
            listbox.delete(index)
        else:
            print("No item selected.")
            return

    def use_item(listbox):
        global WIN_NAME
        global HWND_CHANGED
        selected_index = listbox.curselection()
        if selected_index:
            index = selected_index[0]
            item = listbox.get(index)
            print("Selected item:", item)
            WIN_NAME = item
            HWND_CHANGED = True
            update_title()
        else:
            print("No item selected.")
            return

    if "window_switcher" not in window.children:
        popup = Toplevel(window, name="window_switcher")
        popup.attributes("-topmost", True)
        popup.title("Window Switcher")
        popup.geometry("265x251")

        # Create a Listbox widget
        listbox = Listbox(popup)
        listbox.pack()

        # Add items to the Listbox
        window_names = json_handler.get_window_names()
        for item in window_names:
            listbox.insert(END, item)

        # Create the "Use" button
        use_button = Button(popup, text="Use", command=lambda: use_item(listbox))
        use_button.pack()

        # Create the "Add" button
        add_button = Button(popup, text="Add", command=lambda: add_item(listbox))
        add_button.pack()

        remove_button = Button(
            popup, text="Remove", command=lambda: remove_item(listbox)
        )
        remove_button.pack()
    else:
        window.children["window_switcher"].deiconify()


if WIN_NAME is None:
    messagebox.showinfo(
        "No window selected",
        "Please select a window to be mirrored, or add it if it hasn't been saved yet.",
    )
    switch_window()

menubar = Menu(window)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Switch window", command=switch_window)
filemenu.add_command(
    label=f"Enable auto-popup: {DO_POPUP}", command=lambda: toggle_autopopup(filemenu)
)
filemenu.add_command(
    label=f"Enable auto-minimize: {DO_MINIMIZE}",
    command=lambda: toggle_minimize(filemenu),
)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="Settings", menu=filemenu)

show_frame()
window.config(menu=menubar)
window.mainloop()

# def print_size():
#     while True:
#         x = popup.winfo_width()
#         y = popup.winfo_height()
#         print(x, y)

# t1 = threading.Thread(target=print_size)
# t1.start()
