import os
import pickle

import numpy as np
import torch
from torch.utils.data import Dataset

import config
from datasets.base_dataset import BaseDataset

word_idx = {'02691156': 0,  # airplane
            '03636649': 1,  # lamp
            '03001627': 2}  # chair

idx_class = {0: 'airplane', 1: 'lamp', 2: 'chair'}


class ShapeNet(BaseDataset):
    """
    Dataset wrapping images and target meshes for ShapeNet dataset.
    """

    def __init__(self, file_root, file_list_name, num_points):
        super().__init__()
        self.file_root = file_root
        # Read file list
        with open(os.path.join(self.file_root, "meta", file_list_name + ".txt"), "r") as fp:
            self.file_names = fp.read().split("\n")[:-1]
        self.num_points = num_points

    def __getitem__(self, index):
        label, filename = self.file_names[index].split("_", maxsplit=1)
        with open(os.path.join(self.file_root, "data", label, filename), "rb") as f:
            data = pickle.load(f, encoding="latin1")

        img, pts, normals = data[0].astype(np.float32) / 255.0, data[1][:, :3], data[1][:, 3:]
        pts -= np.array(config.MESH_POS)
        assert pts.shape[0] == normals.shape[0]
        length = pts.shape[0]
        choices = np.resize(np.random.permutation(length), self.num_points)
        pts = pts[choices]
        normals = normals[choices]

        img = torch.from_numpy(np.transpose(img, (2, 0, 1)))
        img_normalized = self.normalize_img(img)

        return {
            "images": img_normalized,
            "images_orig": img,
            "points": pts,
            "normals": normals,
            "labels": label,
            "filename": filename,
            "length": length
        }

    def __len__(self):
        return len(self.file_names)
