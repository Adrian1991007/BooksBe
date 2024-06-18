import cv2
import numpy as np
import base64
from flask import Blueprint, jsonify, request
from decorators import timed

detect_bp = Blueprint("detect", __name__, url_prefix="/detect")


def highlight_face(net, frame, conf_threshold=0.7):
    frame_opencv_dnn = frame.copy()
    frame_height = frame_opencv_dnn.shape[0]
    frame_width = frame_opencv_dnn.shape[1]
    blob = cv2.dnn.blobFromImage(frame_opencv_dnn, 1.0, (300, 300), [104, 117, 123], True, False)

    net.setInput(blob)
    detections = net.forward()
    face_boxes = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * frame_width)
            y1 = int(detections[0, 0, i, 4] * frame_height)
            x2 = int(detections[0, 0, i, 5] * frame_width)
            y2 = int(detections[0, 0, i, 6] * frame_height)
            face_boxes.append([x1, y1, x2, y2])
            cv2.rectangle(frame_opencv_dnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frame_height / 150)), 8)
    return frame_opencv_dnn, face_boxes


@timed
@detect_bp.route("", methods=["POST"])
def detect_gender_and_age():
    face_proto = "opencv/opencv_face_detector.pbtxt"
    face_model = "opencv/opencv_face_detector_uint8.pb"
    age_proto = "opencv/age_deploy.prototxt"
    age_model = "opencv/age_net.caffemodel"
    gender_proto = "opencv/gender_deploy.prototxt"
    gender_model = "opencv/gender_net.caffemodel"

    model_mean_values = (78.4263377603, 87.7689143744, 114.895847746)
    age_list = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
    gender_list = ['Male', 'Female']

    face_net = cv2.dnn.readNet(face_model, face_proto)
    age_net = cv2.dnn.readNet(age_model, age_proto)
    gender_net = cv2.dnn.readNet(gender_model, gender_proto)

    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400

        # Decode base64 image
        image_base64 = data['image']
        image_data = base64.b64decode(image_base64.split(',')[1])
        img_np = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

        if img_np is None:
            return jsonify({'error': 'Invalid image data'}), 400

        # Perform face detection and gender/age estimation
        result_img, face_boxes = highlight_face(face_net, img_np)
        if not face_boxes:
            return jsonify({'error': 'No face detected'})

        results = []
        for faceBox in face_boxes:
            face = img_np[max(0, faceBox[1]):min(faceBox[3], img_np.shape[0]),
                   max(0, faceBox[0]):min(faceBox[2], img_np.shape[1])]

            # Preprocess face for gender estimation
            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), model_mean_values, swapRB=False)

            # Predict gender
            gender_net.setInput(blob)
            gender_preds = gender_net.forward()
            gender = gender_list[gender_preds[0].argmax()]

            # Preprocess face for age estimation
            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), model_mean_values, swapRB=False)

            # Predict age
            age_net.setInput(blob)
            age_preds = age_net.forward()
            age = age_list[age_preds[0].argmax()]

            results.append({'gender': gender, 'age': age[1:-1]})

        return jsonify(results)

    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': 'Internal server error'}), 500
