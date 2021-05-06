# This Python file uses the following encoding: utf-8

# pip install android-auto-play-opencv
import OpenCvTsumtsum as tsum
import win32api, win32con
import pyautogui
import keyboard
import time
from PIL import Image
import numpy

adbpath = 'C:\\platform-tools_r30.0.4-windows\\platform-tools\\'

def main():

    imgArray = numpy.array(Image.open('screenshot_20210506181126.png')) # デバッグ
    route = tsum.routeSearch(imgArray, save=False, view=True)

    # while keyboard.is_pressed('q') == False:
    #     imgArray = pyautogui.screenshot(region=(0,0,500,888))
    #     route = tsum.routeSearch(imgArray)
    #     touchMovePos(route)
    #     time.sleep(2)

    

def touchMovePos(_poslist):
    if len(_poslist) <= 0:
        return

    for index, pos in enumerate(_poslist):
        # 初回
        if index <= 0:
            # タップ開始
            win32api.SetCursorPos(pos)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
        else:
            # 初回以外
            win32api.SetCursorPos(pos)
        time.sleep(0.2)
    # タップ終了
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

if __name__ == '__main__':
    main()
