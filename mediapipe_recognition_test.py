import math
import cv2
import mediapipe as mp
import numpy
from PIL import Image, ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils


def mediapipe_face_detect(image, confidence, resolution):
    with mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=confidence) as face_detection:
        # try:
        #     pil_image = Image.open(file)
        # except Exception as e:
        #     print(e)
        #     return []
        height, width, _ = image.shape[:3]
        # Convert the BGR image to RGB and process it with MediaPipe Face Detection.

        results = face_detection.process(image)

        # Draw face detections of each face.
        return_array = []
        if not results.detections:
            return return_array
        annotated_image = image.copy()
        for idy, detection in enumerate(results.detections):
            # print(detection.score)
            # (x,y)
            LEFT_EYE = (
                int(mp_face_detection.get_key_point(
                    detection=detection, key_point_enum=mp_face_detection.FaceKeyPoint.LEFT_EYE).x * width),
                int(mp_face_detection.get_key_point(
                    detection=detection, key_point_enum=mp_face_detection.FaceKeyPoint.LEFT_EYE).y * height)
            )
            RIGHT_EYE = (
                int(mp_face_detection.get_key_point(
                    detection=detection, key_point_enum=mp_face_detection.FaceKeyPoint.RIGHT_EYE).x * width),
                int(mp_face_detection.get_key_point(
                    detection=detection, key_point_enum=mp_face_detection.FaceKeyPoint.RIGHT_EYE).y * height)
            )
            MOUTH = (
                int(mp_face_detection.get_key_point(
                    detection=detection, key_point_enum=mp_face_detection.FaceKeyPoint.MOUTH_CENTER).x * width),
                int(mp_face_detection.get_key_point(
                    detection=detection, key_point_enum=mp_face_detection.FaceKeyPoint.MOUTH_CENTER).y * height)
            )
            #print(LEFT_EYE, RIGHT_EYE, MOUTH)
            # for pos in [LEFT_EYE, RIGHT_EYE, MOUTH]:
            #    cv2.drawMarker(annotated_image, position=pos, color=(255, 0, 0), markerType=cv2.MARKER_DIAMOND,
            #                   thickness=3)
            # cv2.putText(annotated_image, str(idy), LEFT_EYE, color=(255, 255, 255), fontFace=cv2.FONT_HERSHEY_PLAIN,
            #            fontScale=4, thickness=3)
            dx = (LEFT_EYE[0] + RIGHT_EYE[0]) / 2 - MOUTH[0]
            dy = (LEFT_EYE[1] + RIGHT_EYE[1]) / 2 - MOUTH[1]
            angle = math.degrees(math.fmod(math.pi + math.atan2(dx, dy), math.pi * 2))
            #print(idy, dx, dy, angle)
            CENTER = (((LEFT_EYE[0] + RIGHT_EYE[0]) * 1.3 + MOUTH[0] * 0) / 2.6,
                      ((LEFT_EYE[1] + RIGHT_EYE[1]) * 1.3 + MOUTH[1] * 0) / 2.6)
            ELLIPSIS_SIZE = (
                int(math.sqrt((LEFT_EYE[0] - RIGHT_EYE[0]) ** 2 + (LEFT_EYE[1] - RIGHT_EYE[1]) ** 2) * 2.5),
                int(math.sqrt(((LEFT_EYE[0] + RIGHT_EYE[0]) / 2 - MOUTH[0]) ** 2 +
                              ((LEFT_EYE[1] + RIGHT_EYE[1]) / 2 - MOUTH[1]) ** 2) * 3))
            # cv2.ellipse(annotated_image, (CENTER, ELLIPSIS_SIZE, 180 - angle), color=(0, 0, 255), thickness=3)
            #print(CENTER)
            #print(ELLIPSIS_SIZE)
            affineFunc = cv2.getRotationMatrix2D(CENTER, 360 - angle, scale=1)
            rot = cv2.warpAffine(image, affineFunc, (width, height), borderValue=(255, 255, 255))
            rot_trim = rot[max(int(CENTER[1] - ELLIPSIS_SIZE[1] / 1.7), 0):
                           max(int(CENTER[1] + ELLIPSIS_SIZE[1] / 1.7), 0),
                       max(int(CENTER[0] - ELLIPSIS_SIZE[1] / 1.7), 0):
                       max(int(CENTER[0] + ELLIPSIS_SIZE[1] / 1.7), 0)]
            rt_h, rt_w, _ = rot_trim.shape[:3]
            fixed_rot = Image.new("RGB", (max(rt_w, rt_h), max(rt_w, rt_h)), (255, 255, 255))
            if rt_w != rt_h:
                if rt_w > rt_h:
                    fixed_rot.paste(Image.fromarray(rot_trim), (0, (rt_w - rt_h) // 2))
                else:
                    fixed_rot.paste(Image.fromarray(rot_trim), ((rt_h - rt_w) // 2, 0))
            else:
                fixed_rot = Image.fromarray(rot_trim)

            rot_trim = cv2.resize(numpy.array(fixed_rot), (resolution, resolution), interpolation=cv2.INTER_LANCZOS4)
            # cv2.imshow("rotate" + str(idy), rot_trim)
            return_array.append(cv2.cvtColor(rot_trim, cv2.COLOR_BGR2RGB))
            # cv2.waitKey(0)

        # cv2.imshow('image', annotated_image)
        # cv2.waitKey(0)
        return return_array
