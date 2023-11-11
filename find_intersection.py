import cv2
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image, ImageDraw
from shapely.geometry import Polygon
from ultralytics import YOLO


def get_list_from_xywh(bb:list):
    x_left = bb[0] - bb[2]/2
    x_right = bb[0] + bb[2]/2
    y_up = bb[1] + bb[2]/2
    y_down = bb[1] - bb[2]/2

    return [[int(x_left), int(y_up)],
            [int(x_right), int(y_up)],
            [int(x_left), int(y_down)],
            [int(x_right), int(y_down)]]

def format_swap(bbx:list):
    bbx_1 = get_list_from_xywh(bbx)
    bbx_1_tmp = bbx_1[-1]
    bbx_1[-1] = bbx_1[-2]
    bbx_1[-2] = bbx_1_tmp
    return bbx_1


def calculate_int(human: list, zone: list, draw=False):
    square = human[2] * human[3]
    # Человека перевожим в координаты
    human = format_swap(human) # Пусть это будет человек
    # Зону просто парсим

    poly_1 = Polygon(human)
    poly_2 = Polygon(zone)
    print("Процент вхождения человека в зону")
    if draw:
      plt.plot(*poly_1.exterior.xy)
      plt.plot(*poly_2.exterior.xy)
    return (poly_1.intersection(poly_2).area / square) * 100


model = YOLO("runs/detect/train22/weights/yolov8n.pt")

a = model("D:\Study\Hack_10.11.2023\Monitoring\Php-Angc-K3-8_angc4fr16.jpg")
print()
print(a.boxes)
