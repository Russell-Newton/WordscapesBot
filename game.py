from win32gui import GetWindowRect
from PIL import ImageGrab, Image, ImageDraw
from level import Level
import pytesseract
import cv2
import numpy as np
from typing import List, Callable, Tuple, Optional
import pyautogui as gui


def allowable_chars() -> str:
    return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def whitelist() -> str:
    return "-c tessedit_char_whitelist=" + allowable_chars()

def psm() -> str:
    return "--psm 6"

def join_configs(configs: List[Callable[[], str]]) -> str:
    config = ""
    for config_callable in configs:
        config += config_callable() + " "
    return config[:-1]


class Game:
    def __init__(self, window, save_images: bool = False):
        self.window = window
        self.bbox = GetWindowRect(window)
        self.save_images = save_images
        self.level = None
        self.resize_scale = 0.5
        self.crop_top_proportion = 0.6   # 0.655
        self.crop_bottom_proportion = 0.96 # 1
        self.config = join_configs([psm, whitelist])
        self.boxes = []
        self.smoothing_kernel = np.ones((3, 3), np.float32) / 9

    def load_level(self):
        self.bbox = GetWindowRect(self.window)
        screen: Image = ImageGrab.grab(self.bbox).convert('RGB')
        letter_wheel = screen.crop((0, int(screen.height * self.crop_top_proportion),
                              screen.width, int(screen.height * self.crop_bottom_proportion)))

        thresholded = None
        letters = None

        def find_letters(thresh_low, type):
            nonlocal thresholded
            nonlocal letters
            gray = cv2.cvtColor(np.array(letter_wheel), cv2.COLOR_RGB2GRAY)
            ret, thresholded = cv2.threshold(gray, thresh_low, 255, type)
            thresholded = cv2.resize(thresholded, None, fx=self.resize_scale, fy=self.resize_scale)
            thresholded = cv2.filter2D(thresholded, -1, self.smoothing_kernel)
            cv2.imwrite("thresholded.png", thresholded)

            letters_raw = pytesseract.image_to_string(thresholded, config=self.config)
            letters = []
            for letter in letters_raw:
                if letter in allowable_chars():
                    letters.append(letter)
            if len(letters) < 3:
                raise IndexError()
            self.boxes = [box.split() for box in pytesseract.image_to_boxes(thresholded, config=self.config).split("\n")]
            for box in self.boxes:
                box[1] = int(int(box[1]) / self.resize_scale)
                box[2] = screen.height * self.crop_bottom_proportion - int(int(box[2]) / self.resize_scale)
                box[3] = int(int(box[3]) / self.resize_scale)
                box[4] = screen.height * self.crop_bottom_proportion - int(int(box[4]) / self.resize_scale)
        # print(self.boxes)

        try:
            find_letters(254, cv2.THRESH_BINARY_INV)
            print("Found white letters")
        except IndexError:
            find_letters(0, cv2.THRESH_BINARY)
            print("Found black letters")
        print(letters)
        if self.save_images:
            # print(self.boxes)
            canvas = ImageDraw.Draw(screen)
            try:
                for box in self.boxes:
                    canvas.rectangle([box[1], box[2], box[3], box[4]], outline="red", width=3)
            except:
                pass
            with open("capture.png", 'wb') as file:
                screen.save(file)

        # print(letters)
        self.level = Level(letters)

    def enter_word(self) -> Optional[str]:
        word = self.level.get_word()
        if word is not None:
            boxes_clone = self.boxes.copy()
            sequence = []
            for letter in word:
                index, position = self._get_letter_position(letter, boxes_clone)
                boxes_clone.pop(index)
                sequence.append(position)
            print("{}: {}".format(word, sequence))

            for point in sequence:
                gui.moveTo(point[0], point[1], duration=0.05)
                gui.mouseDown()
            gui.mouseUp()
            return word
        else:
            return None

    def _get_letter_position(self, letter: str, boxes_left: List[Tuple[str, int, int, int, int, str]]) -> Optional[Tuple[int, Tuple[int, int]]]:
        for i in range(len(boxes_left)):
            box = boxes_left[i]
            if box[0] is letter:
                return i, (int((box[1] + box[3]) / 2) + self.bbox[0], int((box[2] + box[4]) / 2) + self.bbox[1])
        return None
