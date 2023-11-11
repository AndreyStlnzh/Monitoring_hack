import os

a = r"D:\Study\Hack_10.11.2023\cameras\DpR-Csp-uipv-ShV-V1\0b1a3d21-2057-4f8f-a69b-23264f438838.jpg"
arr = a.split("\\")

cameras_index = arr.index("cameras")
dir_path = a.split("cameras")[0]


zone_path = os.path.join(dir_path, "danger_zones", f"danger_{arr[cameras_index+1]}.txt")


zone = []
with open(zone_path) as file:
    for line in file:      
        string = line.replace(",", "")
        string = string.replace("[", "")
        string = string.replace("]", "")
        string = string.strip()
        zone.append([int(string.split(" ")[0]), int(string.split(" ")[1])])
print(zone)