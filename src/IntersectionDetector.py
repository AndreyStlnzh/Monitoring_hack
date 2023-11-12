"""Модуль обработки изображений, отрисовки bounding box'ов и предсказаний"""

import cv2
import os
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image, ImageDraw
from shapely.geometry import Polygon
from ultralytics import YOLO
from ensemble_boxes import weighted_boxes_fusion


class IntersectionDetector():
    """Класс для отслеживания пересечений облостей"""

    def __init__(self) -> None:
        """Метод инициализации"""
        self.__model = YOLO("models/YOLOv8n.pt")
        self.__image_path = None
        self.__zone_path = None

        self.__humans_bb = []
        self.__zone_bb = []

        self.intersected = []
        self.__model()  # сделать первое предсказание

    def find_zone_file(self) -> str:
        """
        Метод получения пути до текстового файла опасной зоны;
        :return путь до текстового файла с опасной зоной;
        """
        arr_dirs = self.__image_path.split("/")
        cameras_index = arr_dirs.index("cameras")
        dir_path = self.__image_path.split("cameras")[0]

        zone_path = os.path.join(dir_path, "danger_zones", f"danger_{arr_dirs[cameras_index + 1]}.txt")
        return zone_path

    def read_zone_file(self) -> list:
        """
        Метод считывания зоны из текстового файла в список;
        :return список координат из файла зоны;
        """
        zone = []
        with open(self.__zone_path) as file:
            for line in file:
                string = line.replace(",", "")
                string = string.replace("[", "")
                string = string.replace("]", "")
                string = string.strip()
                zone.append([int(string.split(" ")[0]), int(string.split(" ")[1])])
        return zone

    @staticmethod
    def __get_list_from_xywh(bb: list):
        """
        Форматирование данных из форматы xywh в угловой;
        :param bb - bounding box;
        :return новое представление данных;
        """
        return [[int(bb[0]), int(bb[1])],
                [int(bb[2]), int(bb[1])],
                [int(bb[0]), int(bb[3])],
                [int(bb[2]), int(bb[3])]]

    def __format_swap(self, bbx: list) -> list:
        """Метод для перестановки точек в нужной последовательности"""
        # FIXME: Это надо будет обязательно убрать
        bbx_1 = self.__get_list_from_xywh(bbx)
        bbx_1_tmp = bbx_1[-1]
        bbx_1[-1] = bbx_1[-2]
        bbx_1[-2] = bbx_1_tmp
        return bbx_1

    def __calculate_intersection(self, human: list, draw: bool = False) -> float:
        """
        Метод вычисления площади пересечения;
        :param human - bounding box человека;
        :param draw - режим рисования;
        :return процент тела человека, который пересёкся в опасной зоной;
        """
        square = (human[2] - human[0]) * (human[3] - human[1])
        # Человека переводим в координаты
        human = self.__format_swap(human)

        poly_1 = Polygon(human)
        poly_2 = Polygon(self.__zone_bb)
        if draw:
            plt.plot(*poly_1.exterior.xy)
            plt.plot(*poly_2.exterior.xy)
            plt.show()

        return (poly_1.intersection(poly_2).area / square) * 100

    def calculate_intersections(self, draw: bool = False) -> list:
        """
        Метод получения тех ситуаций, когда тело входит в зону
        более, чем на 15%;
        :param draw - параметр отрисовки ограничивающих рамок;
        :return список истинных или ложных ситуаций нарушения зоны;
        """
        percentage = 15
        intersections_list = []
        for human in self.__humans_bb:
            intersections_list.append(self.__calculate_intersection(human, draw))
        # self.show_all()
        self.intersected = [i > percentage for i in intersections_list]
        return intersections_list

    @staticmethod
    def __draw_by_points(img: list,
                         zone: list,
                         color: tuple = (255, 0, 0),
                         thick: int = 5) -> list:
        """
        Метод отрисовки точек зоны на изображении;
        :param img - исходное изображение;
        :param zone - координаты зоны;
        :param color - цвет зоны;
        :param thick - толщина линий зоны;
        :return изменённое изображение;
        """
        zone.append(zone[0])
        for p in range(len(zone) - 1):
            cv2.line(img,
                     (zone[p][0], zone[p][1]),
                     (zone[p + 1][0], zone[p + 1][1]),
                     color,
                     thick)

        return img

    def show_final_image(self, image_num) -> list:
        """
        Метод отрисовки всех объектов на изображении;
        :return Отрисованное изображение;
        """
        image = cv2.imread(self.__image_path)

        cv2.putText(image, str(image_num), \
                            [100, 200], 
                            cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 255, 255), 10, cv2.LINE_AA)

        i = 0
        for human in self.__humans_bb:
            if self.intersected[i]:
                image = cv2.rectangle(image, (int(human[0]), int(human[1])),
                                      (int(human[2]), int(human[3])), (255, 0, 0), 5)
            else:
                image = cv2.rectangle(image, (int(human[0]), int(human[1])),
                                      (int(human[2]), int(human[3])), (0, 255, 0), 5)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = self.__draw_by_points(image, self.__zone_bb)

        # plt.imshow(image)
        # plt.show()
        return image

    def compute_metrics(boxes, confidences, weights, iou_thr=0.5, skip_box_thr=0.001):
        """
        Computes WBF metrics for bounding boxes and confidences

        :param boxes:       List of lists of bounding boxes prediction for every model in ensemble
        :type boxes:        list
        :param confidences: Confidences for every prediction
        :type confidences:  list
        :param weights:     Weights for every model in ensemble
        :type weights:      list
        :param iou_thr:     IoU threshold
        :type  iou_thr:     float
        """
        labels = [[0 for _ in conf] for conf in confidences]
        res = weighted_boxes_fusion(boxes, confidences, labels,
                                    weights=weights, iou_thr=iou_thr, skip_box_thr=skip_box_thr)
        return [res[0].tolist(), res[1].tolist()]


    def __make_prediction(self) -> None:
        """Метод создания прогноза"""
        pred = self.__model(self.__image_path)
        if pred[0].boxes.xyxy.tolist():
            self.__humans_bb = pred[0].boxes.xyxy.tolist()
        else:
            self.__humans_bb = []

    # TODO: А почему не сделать те нижние методы геттером и сеттером? Есть же
    #       @property. А через него можно и остальное сделать
    def set_image_path(self, image_path) -> None:
        """
        Метод установки путей;
        :param image_path - путь до изображений;
        """
        self.__image_path = image_path
        self.__zone_path = self.find_zone_file()
        self.__zone_bb = self.read_zone_file()
        self.__make_prediction()

    def get_image_path(self) -> str:
        """
        Метод получения пути до изображений;
        :return - путь до изображения;
        """
        return self.__image_path


if __name__ == "__main__":
    # detector = IntersectionDetector(
    #     image_path=r"D:\Study\Hack_10.11.2023\cameras\DpR-Csp-uipv-ShV-V1\0b1a3d21-2057-4f8f-a69b-23264f438838.jpg",
    # )

    detector = IntersectionDetector()
    detector.set_image_path(
        r"D:/Study/Hack_10.11.2023/cameras/DpR-Csp-uipv-ShV-V1/1a16321d-4371-4721-bbc9-ccfc4a17687c.jpg"
    )

    a = detector.calculate_intersections(False)
    print(type(a))
    print(a)
    print([i > 15 for i in a])
