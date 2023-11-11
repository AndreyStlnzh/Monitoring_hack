import cv2
import os
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
from PIL import Image, ImageDraw
from shapely.geometry import Polygon
from ultralytics import YOLO

class IntersectionDetector():
    def __init__(self):
        self.__model = YOLO("models/YOLOv8n.pt")
        self.__image_path = None
        self.__zone_path = None

        self.__humans_bb = []
        self.__zone_bb = []

        self.intersected = []
        self.__model() # сделать первое предсказание


    def find_zone_file(self):
        arr_dirs = self.__image_path.split("/")
        cameras_index = arr_dirs.index("cameras")
        dir_path = self.__image_path.split("cameras")[0]

        zone_path = os.path.join(dir_path, "danger_zones", f"danger_{arr_dirs[cameras_index+1]}.txt")
        return zone_path

    def read_zone_file(self):
        zone = []
        with open(self.__zone_path) as file:
            for line in file:      
                string = line.replace(",", "")
                string = string.replace("[", "")
                string = string.replace("]", "")
                string = string.strip()
                zone.append([int(string.split(" ")[0]), int(string.split(" ")[1])])
        return zone

    def __get_list_from_xywh(self, bb:list):
        return [[int(bb[0]), int(bb[1])],
                [int(bb[2]), int(bb[1])],
                [int(bb[0]), int(bb[3])],
                [int(bb[2]), int(bb[3])]]

    def __format_swap(self, bbx:list):
        bbx_1 = self.__get_list_from_xywh(bbx)
        bbx_1_tmp = bbx_1[-1]
        bbx_1[-1] = bbx_1[-2]
        bbx_1[-2] = bbx_1_tmp
        return bbx_1


    def __calculate_intersection(self, human: list, draw):
        square = (human[2] - human[0]) * (human[3] - human[1])
        # Человека перевожим в координаты
        human = self.__format_swap(human) # Пусть это будет человек
        # Зону просто парсим

        poly_1 = Polygon(human)
        poly_2 = Polygon(self.__zone_bb)
        # print("Процент вхождения человека в зону")
        if draw:
            plt.plot(*poly_1.exterior.xy)
            plt.plot(*poly_2.exterior.xy)
            plt.show()
        
        return (poly_1.intersection(poly_2).area / square) * 100
    

    def calculate_intersections(self, draw=False):
        intersections_list = []
        for human in self.__humans_bb:
            intersections_list.append(self.__calculate_intersection(human, draw))
        # self.show_all()
        self.intersected = [i > 15 for i in intersections_list]
        return intersections_list


    def __draw_by_points(self, img, zone: list, color=(255, 0, 0), thick=5):

        zone.append(zone[0])
        for p in range(len(zone) - 1):
            cv2.line(img,
                    (zone[p][0], zone[p][1]),
                    (zone[p + 1][0], zone[p + 1][1]),
                    color,
                    thick)

        return img


    def show_final_image(self):
        
        image = cv2.imread(self.__image_path)
        
        i = 0
        for human in self.__humans_bb:
            if self.intersected[i]:
                image = cv2.rectangle(image, (int(human[0]), int(human[1])), \
                                  (int(human[2]), int(human[3])), (255, 0, 0), 8)
            else:
                image = cv2.rectangle(image, (int(human[0]), int(human[1])), \
                                    (int(human[2]), int(human[3])), (0, 255, 0), 5)
        
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = self.__draw_by_points(image, self.__zone_bb)

        # plt.imshow(image)
        # plt.show()
        return image


    # def compute_metrics(boxes, confidences, weights, iou_thr=0.5, skip_box_thr=0.001):
    #     """
    #     Computes WBF metrics for bounding boxes and confidences
    #     """
    #     labels = [[0 for _ in conf] for conf in confidences]
    #     res = weighted_boxes_fusion(boxes, confidences, labels,
    #                                 weights=weights, iou_thr=iou_thr, skip_box_thr=skip_box_thr)
    #     return [res[0].tolist(), res[1].tolist()]


    def __make_prediction(self):
        pred = self.__model(self.__image_path)
        if pred[0].boxes.xyxy.tolist():
            self.__humans_bb = pred[0].boxes.xyxy.tolist()
        else:
            self.__humans_bb = []


    def set_image_path(self, image_path):
        self.__image_path = image_path
        self.__zone_path = self.find_zone_file()
        self.__zone_bb = self.read_zone_file()
        self.__make_prediction()
    

    def get_image_path(self):
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

