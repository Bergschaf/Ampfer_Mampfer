import xml.etree.ElementTree as ET
from PIL import Image,ImageDraw



IMG_PATH = "Images/"
XML_PATH = "XML/"

class Img:
    def __init__(self, filename: str,img_path = IMG_PATH,xml_path = XML_PATH):
        self.filename = filename  # Ohne Dateiendung
        self.objects = []
        self.img_path = img_path
        self.xml_path = xml_path
        self.image = Image.open(f"{self.img_path}{filename}.JPG")
        self.marked_image = Image.open(f"{self.img_path}{filename}.JPG")
        self.draw = ImageDraw.Draw(self.marked_image)
        self.parse_xml()

    def reset(self):
        self.marked_image = self.image
        self.draw = ImageDraw.Draw(self.marked_image)

    def parse_xml(self):
        tree = ET.parse(self.xml_path + self.filename + ".xml")
        root = tree.getroot()
        for child in root:
            if child.tag == "object":
                pos = (int(child[4][0].text), int(child[4][1].text), int(child[4][2].text),
                       int(child[4][3].text))  # xmin ymin xmax ymax
                self.objects.append((pos, child[0].text))

    def remove_overlap(self):
        while True:
            change = False
            for index, object in enumerate(self.objects):
                for index2, object2 in enumerate(self.objects[index:]):
                    overlap, smaller = check_overlap(object[0], object2[0])
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

    def save_xml(self):
        root = ET.Element("annotation")
        ET.SubElement(root, "folder").text = "Niedrig"
        ET.SubElement(root, "filename").text = self.filename[:-4]
        ET.SubElement(root,
                      "path").text = f"C:\\Users\\info\\Documents\\.Ampferroboter\\Object_Detection\\Niedrig\\{self.filename}.JPG"

        source = ET.SubElement(root, "source")
        ET.SubElement(source, "database").text = "none"

        size = ET.SubElement(root, "size")
        ET.SubElement(size, "width").text = str(4000)
        ET.SubElement(size, "height").text = str(3000)
        ET.SubElement(size, "depth").text = str(3)

        ET.SubElement(root, "segmented").text = str(0)

        for element in self.objects:
            box = element[0]
            object = ET.SubElement(root, "object")
            ET.SubElement(object, "name").text = element[1]
            ET.SubElement(object, "pose").text = "Unspecified"
            ET.SubElement(object, "truncated").text = str(0)
            ET.SubElement(object, "difficult").text = str(0)

            bndbox = ET.SubElement(object, "bndbox")
            ET.SubElement(bndbox, "xmin").text = str(int(box[0]))
            ET.SubElement(bndbox, "ymin").text = str(int(box[1]))
            ET.SubElement(bndbox, "xmax").text = str(int(box[2]))
            ET.SubElement(bndbox, "ymax").text = str(int(box[3]))

        tree = ET.ElementTree(root)
        tree.write(f"{self.xml_path}{self.filename}_o.xml", encoding="utf-8")


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

if __name__ == '__main__':
    img = Img("198")

    for element in img.objects:
        element = element[0]
        img.draw.rectangle([(element[0], element[1]), (element[2], element[3])], outline="red", width=8)
    img.marked_image.save("Dok/197.JPG")

    img.draw = ImageDraw.Draw(img.image)
    img.remove_overlap()
    for element in img.objects:
        element = element[0]
        img.draw.rectangle([(element[0], element[1]), (element[2], element[3])], outline="red", width=8)
    img.image.save("Dok/197_o.JPG")


