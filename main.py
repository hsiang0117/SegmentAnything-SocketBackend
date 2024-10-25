import os

import matplotlib.pyplot as plt
import torch

os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2
import numpy as np

from segment_anything import sam_model_registry, SamPredictor

sam_checkpoint = "sam_vit_b_01ec64.pth"
model_type = "vit_b"

device = "cuda:0" if torch.cuda.is_available() else "cpu"

sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)

predictor = SamPredictor(sam)

def get_image():
    image = cv2.imread('out.exr', cv2.IMREAD_UNCHANGED)
    image = image[:, :, :3]
    image = cv2.normalize(image, None, 0, 1, cv2.NORM_MINMAX)
    image = np.power(image, 1.0 / 2.2)
    image = (image * 255).astype(np.uint8)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    predictor.set_image(image)
    print("Set image Done")
    return image

def segment(input_point,input_label):
    mask, _, _ = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=False,
    )
    return mask

def show_mask(mask, ax):
    color = np.array([128 / 255, 128 / 255, 128 / 255, 0.4])
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

import socket
import struct

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("",8080))
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
                if data == "PositiveDot":
                    dot = connection.recv(1024).decode()
                    coords = dot.split(" ")
                    input_points.append(coords)
                    input_labels.append(1)
                if data == "NegativeDot":
                    dot = connection.recv(1024).decode()
                    coords = dot.split(" ")
                    input_points.append(coords)
                    input_labels.append(0)
                if data == "Segment":
                    input_points = np.array(input_points)
                    input_labels = np.array(input_labels)
                    mask = segment(input_points,input_labels)
                    plt.imshow(image)
                    show_mask(mask,plt.gca())
                    plt.show()
                if data == "Modify":
                    print("Modify")
                if data == "ExportDone":
                    image = get_image()
                if data == "Clear":
                    image = None
                    mask = None
                    input_points = []
                    input_labels = []

                content = "received"
                buffer = struct.pack(">BB", 1, len(content))
                buffer += content.encode()
                connection.sendall(buffer)
        except ConnectionAbortedError:
            print("Connection aborted")
            connection.close()

    s.close()