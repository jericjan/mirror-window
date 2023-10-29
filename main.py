import argparse
from decimal import Decimal, getcontext
from tkinter import (
    END,
    Button,
    Entry,
    Frame,
    Label,
    Listbox,
    Menu,
    OptionMenu,
    StringVar,
    Tk,
    Toplevel,
    Variable,
    messagebox,
    simpledialog,
)

import numpy as np
from PIL import Image, ImageTk

from classes import JSONHandler, ProcessLister
from iterate import iterate_and_find
from screenshot import get_hwnd, screenshot

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


def convert_fps_ms(num):
    """Convert fps to milliseconds per frame and vice versa"""
    return Decimal(1000) / Decimal(num)


DELAY_MIRRORING = json_handler.get_current("active_delay", integer_ratio=True)
DELAY_NOTHING = json_handler.get_current("paused_delay", integer_ratio=True)


window = Tk()  # Makes main window


def update_title():
    window.wm_title(f"Mirror - [{WIN_NAME}]")


update_title()
window.geometry("500x500")
window.attributes("-topmost", True)

lmain = Label(window)
lmain.pack(anchor="center", expand=True)

error_frame = Frame(window)
status_text = Label(
    error_frame,
    text="Can't find the window. Check if the name is correct or try "
    "running as admin.",
)
status_text.pack()


def refresh():
    global HWND_CHANGED
    HWND_CHANGED = True


refresh_button = Button(error_frame, text="Refresh", command=refresh)
refresh_button.pack()

x = y = w = h = None
prev_shot = None

HWND_CHANGED = True


def show_frame():
    global prev_shot
    global hwnd
    global HWND_CHANGED
    global status_text

    if prev_shot is None:
        error_frame.pack_forget()

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
        error_frame.pack(before=lmain)

        lmain.after(int(DELAY_NOTHING), show_frame)

    elif shot == "focused":
        # print("The window is focused.")

        if type(prev_shot).__name__ == "Image" and DO_MINIMIZE:
            print("MINIMIZING")
            window.iconify()

        lmain.after(int(DELAY_NOTHING), show_frame)

    elif shot == "not enough image data":
        print(f"Looking through all the windows that contain '{WIN_NAME}'")
        hwnd = iterate_and_find(WIN_NAME)
        lmain.after(int(DELAY_NOTHING), show_frame)

    else:
        if prev_shot == "focused" and DO_POPUP:
            print("POPPING UP ")
            window.deiconify()

        img = Image.fromarray(np.array(shot))
        img.thumbnail((window.winfo_width(), window.winfo_height()))

        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)

        lmain.after(int(DELAY_MIRRORING), show_frame)

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


def list_windows(parent_win):
    # region Functions
    def use_item(listbox):
        selected_index = listbox.curselection()
        if selected_index:
            index = selected_index[0]
            item = listbox.get(index)
            print("Selected item:", item)
            selected_window.set(item)
        else:
            print("No item selected.")
            return

    def add_item(listbox):
        # Prompt the user for input
        new_item = selected_window.get()

        # Add the new item to the Listbox
        if new_item:
            listbox.master.master.children["!listbox"].insert(END, new_item)
            # goes up to window_lister, then window_changer, then down to !listbox

        json_handler.add(new_item)

    def insert_sorted_item(listbox, item):
        index = 0
        for i in range(listbox.size()):
            if item < listbox.get(i):
                index = i
                break
            index += 1
        listbox.insert(index, item)

    # Add items to the Listbox
    def populate_listbox(dic=None):
        title_cache = []
        listbox.delete(0, END)
        if dic is None:
            window_names = process_lister.processes
        else:
            window_names = dic
        for hwnd, title in window_names.items():
            if title != "":
                if title not in title_cache:
                    # listbox.insert(END, title)
                    insert_sorted_item(listbox, title)
                    title_cache.append(title)

    def filter_items():
        query = filter_var.get()
        filtered = process_lister.filter(query)
        populate_listbox(filtered)

    # endregion

    if "window_lister" not in window.children:
        popup = Toplevel(parent_win, name="window_lister")
        popup.attributes("-topmost", True)
        popup.title("Window Lister")
        popup.geometry(f"265x251+{parent_win.winfo_x()+10}+{parent_win.winfo_y()+50}")

        # Create a Listbox widget
        listbox = Listbox(popup)

        process_lister = ProcessLister()

        populate_listbox()

        listbox.bind("<<ListboxSelect>>", lambda x: use_item(listbox))

        frame1 = Frame(popup)
        filter_label = Label(frame1, text="Filter:")
        filter_var = StringVar(popup)
        filter_input = Entry(frame1, textvariable=filter_var)

        filter_input.bind("<KeyRelease>", lambda x: filter_items())

        frame2 = Frame(popup)
        selected_label = Label(frame2, text="Selected:")
        selected_window = StringVar(popup)
        input = Entry(frame2, textvariable=selected_window)
        save_btn = Button(frame2, text="Add", command=lambda: add_item(listbox))

        # region Packing
        listbox.pack(fill="both", expand=1)

        filter_label.pack(side="left")
        filter_input.pack(side="left")
        frame1.pack()

        selected_label.pack(side="left")
        input.pack(side="left")
        save_btn.pack(side="left")
        frame2.pack()

        # endregion

    else:
        window.children["window_lister"].deiconify()


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
        popup.geometry(f"265x251+{window.winfo_x()+10}+{window.winfo_y()+50}")

        # Create a Listbox widget
        listbox = Listbox(popup)
        listbox.pack()

        # Add items to the Listbox
        window_names = json_handler.get_window_names()
        for item in window_names:
            listbox.insert(END, item)

        # Create the "Use" button
        listbox.bind("<<ListboxSelect>>", lambda x: use_item(listbox))

        # Create the "Add" button
        # add_button = Button(popup, text="Add", command=lambda: add_item(listbox))
        add_button = Button(popup, text="Add", command=lambda: list_windows(popup))
        add_button.pack()

        remove_button = Button(
            popup, text="Remove", command=lambda: remove_item(listbox)
        )
        remove_button.pack()
    else:
        window.children["window_switcher"].deiconify()


def change_fps():
    options = ["FPS", "Milliseconds per frame"]

    def save_fps():
        global DELAY_MIRRORING
        global DELAY_NOTHING

        a_fps = active_fps_val.get()
        a_type = active_fps_type.get()
        p_fps = paused_fps_val.get()
        p_type = paused_fps_type.get()

        getcontext().prec = 28

        active_ms = a_fps if a_type == options[1] else convert_fps_ms(a_fps)
        paused_ms = p_fps if p_type == options[1] else convert_fps_ms(p_fps)

        DELAY_MIRRORING = active_ms
        DELAY_NOTHING = paused_ms
        json_handler.set_current("active_delay", active_ms, integer_ratio=True)
        json_handler.set_current("paused_delay", paused_ms, integer_ratio=True)

    if "fps_switcher" not in window.children:
        popup = Toplevel(window, name="fps_switcher")
        popup.attributes("-topmost", True)
        popup.title("FPS Changer")
        popup.geometry(f"265x251+{window.winfo_x()+10}+{window.winfo_y()+50}")

        frame1 = Frame(popup)

        active_fps_label = Label(popup, text="FPS for when window is tabbed out:")

        active_fps_type = StringVar(popup)
        active_fps_type.set(options[0])
        active_fps_dropdown = OptionMenu(frame1, active_fps_type, *options)

        getcontext().prec = 6

        active_fps_val = Variable(popup)
        active_fps_val.set(convert_fps_ms(DELAY_MIRRORING))
        active_fps_input = Entry(frame1, textvariable=active_fps_val)

        frame2 = Frame(popup)

        pause_fps_label = Label(popup, text="FPS for when window is focused:")

        paused_fps_type = StringVar(popup)
        paused_fps_type.set(options[0])
        paused_fps_dropdown = OptionMenu(frame2, paused_fps_type, *options)

        paused_fps_val = Variable(popup)
        paused_fps_val.set(convert_fps_ms(DELAY_NOTHING))
        paused_fps_input = Entry(frame2, textvariable=paused_fps_val)

        save_btn = Button(popup, text="Save", command=save_fps)

        active_fps_label.pack()
        active_fps_dropdown.pack(side="left")
        active_fps_input.pack(side="left")
        frame1.pack()
        pause_fps_label.pack()
        paused_fps_dropdown.pack(side="left")
        paused_fps_input.pack(side="left")
        frame2.pack()
        save_btn.pack()

    else:
        window.children["fps_switcher"].deiconify()


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
filemenu.add_command(
    label="Change FPS",
    command=change_fps,
)
filemenu.add_separator()
filemenu.add_command(
    label="Wrong window?",
    command=lambda: messagebox.showinfo(
        "Wrong window?",
        "If you have multiple windows with the same name, simply focus the window you want to mirror and refresh.",
    ),
)
filemenu.add_command(label="Exit", command=window.quit)
menubar.add_cascade(label="Settings", menu=filemenu)
menubar.add_cascade(label="Refresh", command=refresh)

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
