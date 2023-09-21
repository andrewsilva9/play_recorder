from PIL import Image

import win32gui
import mss
import time
import numpy as np
import cv2

# def set_pixel(img, w, x, y, rgb=(0, 0, 0)):
#     # From https://github.com/BoboTiG/python-mss/issues/55
#     """
#     Set a pixel in a, RGB byte array
#     """
#     pos = (x * w + y) * 3
#     if pos >= len(img): return img  # avoid setting pixel outside of frame
#     img[pos:pos + 3] = rgb
#     return img

template = cv2.imread('../../imitation_rl_games/individual_explorations/test_images/cursor2.png', cv2.IMREAD_UNCHANGED)
w = template.shape[1]
h = template.shape[0]
# # resized = template[::4, ::4]
# width = int(w * 25 / 100)
# height = int(h * 25 / 100)
# dim = (width, height)
# resized = cv2.resize(template, dim, interpolation=cv2.INTER_AREA)
if template.shape[2] < 4:
        template = np.concatenate(
            [
                template,
                np.ones((template.shape[0], template.shape[1], 1), dtype = template.dtype) * 255
            ],
            axis = 2,
        )
overlay_image = template[..., :3]
mask = template[..., 3:] / 255.0
mask[overlay_image[:, :, 2] < 100] = 0


def transparent_cursor(img, boundaries):
    flags, hcursor, (cx, cy) = win32gui.GetCursorInfo()
    # cursor = get_cursor(hcursor)
    cx = cx - boundaries['left']
    cy = cy - boundaries['top']
    if cx > 0 and cy > 0:
        try:
            img[cy:cy + h, cx:cx + w] = (1.0 - mask) * img[cy:cy + h, cx:cx + w] + mask * overlay_image
            return img
        except ValueError as e:
            print(e)
            return img
    return img



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

def screen_record(recording_object, window_title):
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    times = []
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
            out = cv2.VideoWriter("screenshots/output.avi", fourcc, 10, (854, 480))  # (512, 288))
            last_frame = time.time()
            while recording_object.recording:
                # if time.time() - last_frame < 1/24:
                #     continue
                img = np.asarray(sct.grab(bounds))[:, :, [0, 1, 2]]
                last_frame = time.time()
                # img_with_mouse = add_mouse(img, bounds)

                img_with_mouse = transparent_cursor(img, bounds)
                img_with_mouse = cv2.resize(img_with_mouse, (854, 480))  # (512, 288))

                # img_with_mouse = cv2.putText(img_with_mouse,
                #                              str(last_frame),
                #                              (20, 20),
                #                              cv2.FONT_HERSHEY_PLAIN,
                #                              fontScale=2,
                #                              color=(255, 255, 255))
                out.write(img_with_mouse)
                times.append(f'{last_frame},')

            out.release()
            with open('screenshots/timestamps.txt', 'w') as f:
                f.writelines(times)

        else:
            print('Window not found!')


def screen_save(queue):
    output = "screenshots/{}.jpg"
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter("output.avi", fourcc, 24, tuple(w.size))
    while True:
        img = queue.get()
        if img is None:
            print(f'Nothing in queue')
            return None
        img.save(output.format(time.time()))


if __name__ == "__main__":
    # Debug file saving
    import os
    pathname = 'C:\\Users\\asilv\\Documents\\Projects\\play_recorder\\play_recorder\\jaina_video_capture.txt'
    if '.' in pathname:
        pathname = pathname.split('.')[0]
    os.rename('screenshots/output.avi', f'{pathname}_video.avi')
    os.rename('screenshots/timestamps.txt', f'{pathname}_video_timestamps.txt')
    # Debug timestamp collection
    timestamps = []
    with open('./screenshots/timestamps.txt', 'r') as f:
        timestamps = f.readlines()[0]
    timestamps = [float(x) for x in timestamps.split(',') if len(x)>0]
    cap = cv2.VideoCapture('./screenshots/output.avi')
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_timestamps = [cap.get(cv2.CAP_PROP_POS_MSEC)]
    calc_timestamps = []
    while (cap.isOpened()):
        frame_exists, curr_frame = cap.read()
        next_t = timestamps[len(calc_timestamps)]
        if frame_exists:
            video_timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC))
            t_diff = 0
            if len(calc_timestamps) > 0:
                t_diff = next_t - last_t
            calc_timestamps.append(t_diff)
            last_t = next_t
            cv2.imshow('scren', curr_frame)
            cv2.waitKey(0)

# img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX").resize((512, 288))
# img_with_mouse = Image.fromarray(img_with_mouse).resize((512, 288))
# image_buffer.append([last_frame, img_with_mouse])
# queue.put(img_with_mouse)
# queue.put(None)
