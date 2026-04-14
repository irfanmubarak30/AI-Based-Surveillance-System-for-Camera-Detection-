import torch
import cv2
import os
import time
import winsound  # For beep sound (Windows)
import uuid  # For unique filenames
from flask import Flask, Response, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
from ultralytics import YOLO  # YOLOv8 model import

# Load the YOLOv8 model

device = "cuda" #if torch.cuda.is_available() else "cpu"
model = YOLO(r"C:\Users\irfan\Documents\TAPACD\T.A.P.A.C.D\backend\best8m.pt").to(device)
# Setup image capture folder
CAPTURE_FOLDER = os.path.abspath("captured_images")
os.makedirs(CAPTURE_FOLDER, exist_ok=True)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Allow frontend only

# Open webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("Cannot open webcam")

# Detection settings
detection_start_time = None  # Track when phone detection starts
capture_threshold = 7  # Seconds the phone must be detected continuously

def capture_image(frame):
    """ Captures an image and saves it with a unique filename. """
    filename = f"capture_{uuid.uuid4().hex}.jpg"  # Unique filename
    file_path = os.path.join(CAPTURE_FOLDER, filename)
    cv2.imwrite(file_path, frame)
    winsound.Beep(1000, 500)  # Beep sound when capturing
    print(f"📸 Image captured: {file_path}")
    return filename

def gen_frames():
    """ Captures frames from the webcam, runs YOLOv8 detection, and streams frames with bounding boxes. """
    global detection_start_time
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLOv8 object detection
        results = model(frame)
        detections = results[0].boxes.data.cpu().numpy()  # Extract detection results

        phone_detected = False  # Track if phone is detected

        for detection in detections:
            if len(detection) >= 6:  # Ensure at least 6 elements (xyxy, conf, class)
                x1, y1, x2, y2, conf, cls = detection
                
                if conf > 0.2:  
                    phone_detected = True
                    
                    # Draw bounding box around detected phone
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"Conf: {conf:.2f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Capture image if phone is continuously detected for `capture_threshold` seconds
        if phone_detected:
            if detection_start_time is None:
                detection_start_time = time.time()
            elif time.time() - detection_start_time >= capture_threshold:
                capture_image(frame)
                detection_start_time = None
        else:
            detection_start_time = None

        # Encode and send frame as a live video stream
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """ Endpoint for live video feed. """
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/logs', methods=['GET'])
def get_logs():
    """ Endpoint to return list of captured images. """
    images = os.listdir(CAPTURE_FOLDER)
    return jsonify({"images": images})

@app.route('/images/<filename>')
def get_image(filename):
    """ Endpoint to serve saved images. """
    return send_from_directory(CAPTURE_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
