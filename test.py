from exif import Image


def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees

def get_flight_yaw_altitude_coords(image_path):
    with open(image_path, "rb") as img:

        img_text = img.read()
        image = Image(img_text)
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


print(get_flight_yaw_altitude_coords("Images/198.JPG"))