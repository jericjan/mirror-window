from ctypes import windll

import pywintypes
import win32gui
import win32ui
from PIL import Image


def is_window_focused(hwnd):
    return hwnd == win32gui.GetForegroundWindow()


def get_hwnd(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    return hwnd


def screenshot(hwnd):
    print(f"Window ID: {hwnd}", end=", ")

    focused = is_window_focused(hwnd)
    print(f"Focused: {focused}")
    if focused:
        return "focused"

    # class_name = win32gui.GetClassName(hwnd)
    # print(f"Class name: {class_name}", end=", ")

    # Change the line below depending on whether you want the whole window
    # or just the client area.
    # left, top, right, bot = win32gui.GetClientRect(hwnd)
    try:
        left, top, right, bot = win32gui.GetWindowRect(hwnd)
    except pywintypes.error as e:
        print("GetWindowRect error:\n"+e)
        return
    w = right - left
    h = bot - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)

    saveDC.SelectObject(saveBitMap)

    # Change the line below depending on whether you want the whole window
    # or just the client area.
    # result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 1)
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
    print(f"PrintWindow result: {result}")

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    try:
        im = Image.frombuffer(
            "RGB",
            (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
            bmpstr,
            "raw",
            "BGRX",
            0,
            1,
        )
    except ValueError as e:
        return str(e)
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    if result == 1:
        return im
    else:
        print("PrintWindow failed.")
        return im