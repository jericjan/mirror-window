import win32gui

from screenshot import screenshot


def enum_windows_callback(hwnd, windows):
    windows[hwnd] = win32gui.GetWindowText(hwnd)


def iterate_and_find(window_name):
    windows = {}
    win32gui.EnumWindows(enum_windows_callback, windows)

    for hwnd, title in windows.items():
        if title == window_name:
            shot = screenshot(hwnd)
            if shot != "not enough image data":
                return hwnd
