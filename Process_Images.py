import Remove_Overlap

from PIL import Image, ImageDraw, ImageFont
import os


IMG_PATH = "Images/"
XML_PATH = "XML/"

if __name__ == '__main__':
    imglist = [i[:-4] for i in os.listdir(IMG_PATH)]
    for f in os.listdir(XML_PATH):
        print(f)
        if f[:-4] not in imglist or f != "197.xml":
            continue
        img = Remove_Overlap.Img(f[:-4],img_path=IMG_PATH,xml_path=XML_PATH)
        for element in img.objects:
            element = element[0]
            img.draw.rectangle([(element[0], element[1]), (element[2], element[3])], outline="red", width=10)
        img.marked_image.show()
        x = input()
        img.reset()
        img.remove_overlap()
        for element in img.objects:
            element = element[0]
            img.draw.rectangle([(element[0], element[1]), (element[2], element[3])], outline="red", width=10)
        img.marked_image.show()
        img.save_xml()
        x = input()



        #img.image.save("drive/MyDrive/Object_detection_Data/Testbilder_Drohne_Ergebnis/" + str(target["filename"])[
         #                                                                              :-4] + "_V2.JPG")
