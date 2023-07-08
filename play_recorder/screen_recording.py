from PIL import Image

import win32gui
import mss
import time
import numpy as np


# def set_pixel(img, w, x, y, rgb=(0, 0, 0)):
#     # From https://github.com/BoboTiG/python-mss/issues/55
#     """
#     Set a pixel in a, RGB byte array
#     """
#     pos = (x * w + y) * 3
#     if pos >= len(img): return img  # avoid setting pixel outside of frame
#     img[pos:pos + 3] = rgb
#     return img


def add_mouse(img, boundaries):
    # From https://github.com/BoboTiG/python-mss/issues/55
    flags, hcursor, (cx, cy) = win32gui.GetCursorInfo()
    # cursor = get_cursor(hcursor)
    cx = cx - boundaries['left']
    cy = cy - boundaries['top']
    if cx > 0 and cy > 0:
        try:

            img[cy:cy + 36, cx:cx + 36, :3] += 100  # += cursor
            img = np.clip(img, 0, 255)
        except ValueError:
            print(img.shape)
            return img
    return img
    # cursor_mean = cursor.mean(-1)
    # where = np.where(cursor_mean > 0)
    # for x, y in zip(where[0], where[1]):
    #     rgb = [x for x in cursor[x, y]]
    #     img = set_pixel(img, w, x + cy, y + cx, rgb=rgb)
    # return img


# def get_cursor(hcursor):
#     # From https://github.com/BoboTiG/python-mss/issues/55
#     info = win32gui.GetCursorInfo()
#     hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
#     hbmp = win32ui.CreateBitmap()
#     hbmp.CreateCompatibleBitmap(hdc, 36, 36)
#     hdc = hdc.CreateCompatibleDC()
#     hdc.SelectObject(hbmp)
#     hdc.DrawIcon((0, 0), hcursor)
#
#     bmpinfo = hbmp.GetInfo()
#     bmpbytes = hbmp.GetBitmapBits()
#     bmpstr = hbmp.GetBitmapBits(True)
#     im = np.array(Image.frombuffer(
#         'RGB',
#         (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
#         bmpstr, 'raw', 'BGRX', 0, 1))
#
#     win32gui.DestroyIcon(hcursor)
#     win32gui.DeleteObject(hbmp.GetHandle())
#     hdc.DeleteDC()
#     return im
#
#

def screen_record(recording_object, window_title, queue):
    print(f'In recording with window {window_title}')
    with mss.mss(with_cursor=True) as sct:
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            print(f'Found window {hwnd}')
            win32gui.SetForegroundWindow(hwnd)
            x_b, y_b, width, height = win32gui.GetClientRect(hwnd)
            x, y = win32gui.ClientToScreen(hwnd, (x_b, y_b))
            bounds = {'top': y, 'left': x, 'width': width, 'height': height}
            print(f'Found bounds at {bounds}')
            while recording_object.recording:
                img = np.asarray(sct.grab(bounds))[:, :, [2, 1, 0]]
                # img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX").resize((512, 288))
                img_with_mouse = add_mouse(img, bounds)
                img_with_mouse = Image.fromarray(img_with_mouse).resize((512, 288))
                queue.put(img_with_mouse)
            queue.put(None)
        else:
            print('Window not found!')


def screen_save(queue):
    output = "screenshots/{}.jpg"
    while True:
        img = queue.get()
        if img is None:
            print(f'Nothing in queue')
            return None
        img.save(output.format(time.time()))

