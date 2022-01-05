"""
Drohne niedrig Test
"""
import logging
import numpy as np
import torch
import torch.utils.data
import PIL
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from engine import train_one_epoch, evaluate
import utils
import transforms as T
import xml.etree.ElementTree as ET
import os
from PIL import ImageDraw, Image

bilderp = "C:/Users/info/Documents/.Ampferroboter/Object_Detection/Niedrig"


class Dataloader(torch.utils.data.Dataset):
    def __init__(self, transforms=None):
        self.Bilder = bilderp
        self.pdir = sorted(os.listdir(self.Bilder))
        self.Data = {}
        self.Boxes = []
        self.Transforms = transforms

    def __getitem__(self, idx):  # returns a dictionary with filenames as keys
        # only returns the labeled pictures as a list: [Boxes,RGB-Image]

        img = Image.open(self.Bilder + self.pdir[idx]).convert("RGB")
        target = {}
        if self.Transforms is not None:
            img, target = self.Transforms(img, target)
        return img, target

    def __len__(self):
        return int(len(self.pdir))


def get_model(num_classes):
    # load an object detection model pre-trained on COCO
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    # get the number of input features for the classifier
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    # replace the pre-trained head with a new on
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)

    if os.path.isfile("G:/Meine Ablage/Object_detection_Data/Netze/model_drohne_niedrig_V2.pt"):
        print("---loaded model---")
        model.load_state_dict(torch.load("G:/Meine Ablage/Object_detection_Data/Netze/model_drohne_niedrig_V2.pt"))
    else:
        logging.warning("model not found")
    return model


def get_transform(train):
    transforms = []
    transforms.append(T.ToTensor())
    if train:
        # during training, randomly flip the training images
        transforms.append(T.RandomHorizontalFlip(0.5))
    return T.Compose(transforms)


dataset = Dataloader(transforms=get_transform(train=True))
torch.manual_seed(1)
indices = torch.randperm(len(dataset)).tolist()
dataset = torch.utils.data.Subset(dataset, indices)
data_loader = torch.utils.data.DataLoader(
    Dataloader(transforms=get_transform(train=True)), batch_size=2, shuffle=True, num_workers=2,
    collate_fn=utils.collate_fn)

loaded_model = get_model(num_classes=2)


for idx in range(20):

    img, _ = dataset[idx]

    # put the model in evaluation mode
    loaded_model.eval()
    with torch.no_grad():
        prediction = loaded_model([img])

    for element in range(len(prediction[0]["boxes"])):
        boxes = prediction[0]["boxes"][element].cpu().numpy()
        score = np.round(prediction[0]["scores"][element].cpu().numpy(),
                         decimals=4)

        if score > 0.6:
            print(boxes)



# Tutorial: https://towardsdatascience.com/building-your-own-object-detector-pytorch-vs-tensorflow-and-how-to-even-get-started-1d314691d4ae