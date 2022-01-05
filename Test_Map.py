
bilderp = "drive/MyDrive/Bilder/"
targetp = "drive/MyDrive/Koordinaten/"


class Dataloader(torch.utils.data.Dataset):
    def __init__(self, transforms=None):
        self.Bilder = bilderp
        self.pdir = sorted(os.listdir(self.Bilder))
        self.Data = {}
        self.Boxes = []
        self.Transforms = transforms

    def __getitem__(self, idx):  # returns a dictionary with filenames as keys
        img = Image.open(self.Bilder + self.pdir[idx]).convert("RGB")
        target = {"filename": self.pdir[idx]}
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

    if os.path.isfile("drive/MyDrive/Object_detection_Data/Netze/model_drohne_niedrig_V2.pt"):
        print("---loaded model---")
        model.load_state_dict(torch.load("drive/MyDrive/Object_detection_Data/Netze/model_drohne_niedrig_V2.pt"))
    else:
        logging.warning("model not found")
    return model


def get_transform():
    transforms = []
    transforms.append(T.ToTensor())
    return T.Compose(transforms)


class Img:
    def __init__(self, filename: str, prediction):
        self.filename = filename  # Ohne Dateiendung
        self.get_objects(prediction)

    def get_objects(prediciton):
        self.objects = []
        for element in range(len(prediction[0]["boxes"])):
            boxes = prediction[0]["boxes"][element].cpu().numpy()
            pos = (int(boxes[0]), int(boxes[1]), int(boxes[2]), int(boxes[3]))
            self.objects.append(pos)

    def remove_overlap(self):
        while True:
            change = False
            for index, object in enumerate(self.objects):
                for index2, object2 in enumerate(self.objects[index:]):
                    overlap, smaller = check_overlap(object, object2)
                    if overlap > 0.8:
                        change = True

                        try:
                            if smaller == 1:
                                self.objects.remove(object)
                            else:
                                self.objects.remove(object2)
                        except ValueError:
                            pass
            if not change:
                break


def check_overlap(pos1, pos2):
    difx = 0
    if pos2[0] < pos1[0] < pos2[2]:
        difx = pos2[2] - pos1[0]
        if pos2[0] < pos1[2] < pos2[2]:
            difx = pos2[2] - pos2[0]

    elif pos1[0] < pos2[0] < pos1[2]:
        difx = pos1[2] - pos2[0]
        if pos1[0] < pos2[2] < pos1[2]:
            difx = pos1[2] - pos1[0]

    dify = 0
    if pos2[1] < pos1[1] < pos2[3]:
        dify = pos2[3] - pos1[1]
        if pos2[1] < pos1[3] < pos2[3]:
            dify = pos2[3] - pos2[1]

    elif pos1[1] < pos2[1] < pos1[3]:
        dify = pos1[3] - pos2[1]
        if pos1[1] < pos2[3] < pos1[3]:
            dify = pos1[3] - pos1[1]

    overlap = difx * dify

    A_pos1 = (pos1[2] - pos1[0]) * (pos1[3] - pos1[1])
    A_pos2 = (pos2[2] - pos2[0]) * (pos2[3] - pos2[1])

    return (overlap / A_pos1, 1) if A_pos1 < A_pos2 else (overlap / A_pos2, 2)


def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def get_flight_yaw_altitude_coords(image_path):
    with open(image_path, "rb") as img:

        img_text = img.read()
        image = EImage(img_text)
        coords = (decimal_coords(image.gps_latitude,
                                 image.gps_latitude_ref),
                  decimal_coords(image.gps_longitude,
                                 image.gps_longitude_ref))

        start_pos = img_text.find(b"FlightYawDegree=") + 17
        for i, b in enumerate(img_text[start_pos:]):
            if b == 34:
                end_pos = i
                break
        yaw = float(img_text[start_pos:end_pos + start_pos])
        start_pos = img_text.find(b"RelativeAltitude=") + 18
        for i, b in enumerate(img_text[start_pos:]):
            if b == 34:
                end_pos = i
                break
        alt = float(img_text[start_pos:end_pos + start_pos])
        return yaw, alt, coords


def get_Angle_from_Camera(x: int, y: int):
    new_x = x - 2000
    new_y = y - 1500
    dist = 0
    if new_x != 0 and new_y != 0:
        dist = math.sqrt(pow(new_x, 2) + pow(new_y, 2))
    return dist, math.atan2(y - 1500, x - 2000) + math.pi / 2


def parse_boxes(boxes):
    ampfer_list = []
    for box in boxes:
        avgx = int((box[0] + box[2]) / 2)
        avgy = int((box[1] + box[3]) / 2)
        ampfer_list(avgx, avgy)
    return ampfer_list


def get_Ampfer_Cords(filename, boxes, Img_dir):
    IMG_PATH = f"{Img_dir}{filename}.JPG"
    ampfer_coords = []
    yaw, alt, coords = get_flight_yaw_altitude_coords(IMG_PATH)
    meter_per_pixel = (alt * math.tan(math.radians(39.5))) / math.sqrt(pow(2000, 2) + pow(1500, 2))
    for x, y in parse_xml(boxes):
        dist_pixel, angle_from_middle = get_Angle_from_Camera(x, y)
        abs_angle = math.radians(yaw) + angle_from_middle
        dist = dist_pixel * meter_per_pixel
        ampfer_coords.append(inverse_haversine(coords, dist, abs_angle, unit=haversine.Unit.METERS))
    return ampfer_coords


if __name__ == "__main__":
    dataset = Dataloader(transforms=get_transform())
    torch.manual_seed(1)
    indices = torch.randperm(len(dataset)).tolist()
    dataset = torch.utils.data.Subset(dataset, indices)
    data_loader = torch.utils.data.DataLoader(
        Dataloader(transforms=get_transform()), batch_size=2, shuffle=False, num_workers=2,
        collate_fn=utils.collate_fn)
    loaded_model = get_model(num_classes=2).eval()

    for idx in range(os.listdir(bilderp)):
        img, filename = dataset[idx]

        with torch.no_grad():
            prediction = loaded_model([img])

            pic_name = filename["filename"]
            img = Image(pic_name[:-4], prediction)
            img.remove_overlap()
            cordslist = get_Ampfer_Cords(pic_name[:-4], img.objects, bilderp)
            json.dumps(cordslist)
            with open(targetp + pic_name[:-4].json, "w") as f:
                f.write(cordslist)
            print(pic_name + " done!")


