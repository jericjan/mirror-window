import win32gui

from screenshot import screenshot


def enum_windows_callback(hwnd, windows):
    windows[hwnd] = win32gui.GetWindowText(hwnd)


def iterate_and_find(window_name):

    for hwnd, title in list_all_hwnd_title().items():
        if title == window_name:
            shot = screenshot(hwnd)
            if shot != "not enough image data":
                return hwnd

def list_all_hwnd_title():
    windows = {}
    win32gui.EnumWindows(enum_windows_callback, windows)
    return windows