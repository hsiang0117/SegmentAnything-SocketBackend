import matplotlib.pyplot as plt
import torch

from tilemodifier import *

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"
import cv2
import numpy as np

from segment_anything import sam_model_registry, SamPredictor

sam_checkpoint = "models/sam_vit_b_01ec64.pth"
model_type = "vit_b"

device = "cuda:0" if torch.cuda.is_available() else "cpu"

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

predictor = SamPredictor(sam)


def get_image():
    img = cv2.imread('out.exr', cv2.IMREAD_UNCHANGED)
    img = img[:, :, :3]
    img = cv2.normalize(img, None, 0, 1, cv2.NORM_MINMAX)
    img = np.power(img, 1.0 / 2.2)
    img = (img * 255).astype(np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    predictor.set_image(img)
    return img


def segment(input_point, input_label):
    mask, _, _ = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=False,
    )
    return mask


def show_mask(mask, ax):
    color = np.array([255 / 255, 255 / 255, 255 / 255, 0.5])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    ax.imshow(mask_image)


def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels == 1]
    neg_points = coords[labels == 0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green', marker='*', s=marker_size, edgecolor='white',
               linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red', marker='*', s=marker_size, edgecolor='white',
               linewidth=1.25)


def save_mask(mask):
    color = np.array([255 / 255, 255 / 255, 255 / 255, 0.5])
    h, w = mask.shape[-2:]
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    plt.imsave("./mask.png", mask_image)


import socket
import struct

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 8080))
s.listen(1)

if __name__ == '__main__':
    while True:
        connection, address = s.accept()
        print("Connected by:", address)
        image = None
        mask = None
        input_points = []
        input_labels = []
        try:
            while True:
                data = connection.recv(1024)
                data = data.decode()
                content = ""
                if data == "PositiveDot":
                    dot = connection.recv(1024).decode()
                    coords = dot.split(" ")
                    coords[0] = float(coords[0])
                    coords[1] = float(coords[1])
                    input_points.append(coords)
                    input_labels.append(1)
                    print(coords)
                if data == "NegativeDot":
                    dot = connection.recv(1024).decode()
                    coords = dot.split(" ")
                    coords[0] = float(coords[0])
                    coords[1] = float(coords[1])
                    input_points.append(coords)
                    input_labels.append(0)
                    print(coords)
                if data == "Segment":
                    input_points_array = np.array(input_points)
                    input_labels_array = np.array(input_labels)
                    mask = segment(input_points_array, input_labels_array)
                    save_mask(mask)
                    mask = mask.tolist()[0]
                    mask = analyse_mask(mask)
                    content = "SegmentDone"
                if data == "Modify":
                    terrain_folder_path = connection.recv(1024).decode()
                    lod = connection.recv(1024).decode()
                    bottom_left_and_top_right = connection.recv(1024).decode().split(" ")
                    offset = connection.recv(1024).decode().split(" ")
                    offset[0] = int(offset[0])
                    offset[1] = int(offset[1])
                    modify_tiles(mask, terrain_folder_path, lod, bottom_left_and_top_right, offset)
                if data == "ExportDone":
                    image = get_image()
                    content = "SetImageDone"
                if data == "Clear":
                    image = None
                    mask = None
                    input_points = []
                    input_labels = []

                if content == "":
                    content = "received"
                buffer = struct.pack(">BB", 1, len(content))
                buffer += content.encode()
                connection.sendall(buffer)
        except ConnectionAbortedError:
            print("Connection aborted")
            connection.close()

    s.close()
