from flask import Flask, render_template, Response
from ultralytics import YOLO
import cv2
import pygame
import serial
import time
import smtplib
from email.message import EmailMessage
import threading

app = Flask(__name__)

MODEL_PATH = "best.pt"

# ESP32-CAM stream URL
ESP32_CAM_URL = "http://10.30.198.148:81/stream"  #only ip see it in AIcam serial monitor by click reset back side

# ESP32-WROOM COM port
SERIAL_PORT = "COM5"
BAUD_RATE = 115200

CONF_THRES = 0.70
ALERT_COOLDOWN = 30

SENDER_EMAIL = "11b06sivabalan@gmail.com"
APP_PASSWORD = "eael ocdp bjej rsjb" #change ctrl+shift+t
RECEIVER_EMAIL = "newrajastudio.kpr_bec27@mepcoeng.ac.in"

model = YOLO(MODEL_PATH)

last_alert_time = 0
pig_detected_global = False
prev_detected = False   

try:
    esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("ESP32-WROOM connected")
except:
    esp32 = None
    print("ESP32-WROOM not connected")

pygame.mixer.init()


def play_predator_sound():
    try:
        pygame.mixer.music.load("predator.mp3")
        pygame.mixer.music.play()
    except Exception as e:
        print("Sound error:", e)

def send_email_alert():
    try:
        msg = EmailMessage()
        msg["Subject"] = "Wild Boar Detected Alert"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg.set_content("Alert: Wild boar detected. Deterrent activated.")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)

        print("Email alert sent")

    except Exception as e:
        print("Email error:", e)

def trigger_deterrent():
    global last_alert_time

    if esp32:
        esp32.write(b'1\n')
        print(">>> SENT 1")
        esp32.flush()
        print("Sent 1 to ESP32")

    current_time = time.time()
    if current_time - last_alert_time > ALERT_COOLDOWN:
        last_alert_time = current_time

        threading.Thread(target=play_predator_sound).start()
        threading.Thread(target=send_email_alert).start()
# def trigger_deterrent():
#     global last_alert_time

#     current_time = time.time()

#     if current_time - last_alert_time > ALERT_COOLDOWN:
#         last_alert_time = current_time

#         print("Sending 1 to ESP32")
#         if esp32:
#             esp32.write(b'1')
#             esp32.flush()

#         threading.Thread(target=play_predator_sound).start()
#         threading.Thread(target=send_email_alert).start()
def stop_deterrent():
    if esp32:
        esp32.write(b'0\n')
        esp32.flush()
        print("Sent 0 to ESP32")
# def stop_deterrent():
#     print("Sending 0 to ESP32")
#     if esp32:
#         esp32.write(b'0')
#         esp32.flush()

def generate_frames():
    global pig_detected_global, prev_detected

    # cap = cv2.VideoCapture(ESP32_CAM_URL, cv2.CAP_FFMPEG)
    cap = cv2.VideoCapture(ESP32_CAM_URL)

    if not cap.isOpened():
        print("Cannot open ESP32-CAM stream")
        return

    while True:
        success, frame = cap.read()

        if not success:
            print("Frame not received, reconnecting...")
            cap.release()
            time.sleep(1)
            cap = cv2.VideoCapture(ESP32_CAM_URL, cv2.CAP_FFMPEG)
            continue

        results = model(frame, conf=CONF_THRES, verbose=False)

        pig_detected = False

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names[cls_id]
                # print("Detected:", class_name, conf)
                # if class_name.lower() in ["pig", "wild boar", "boar"]:
                #     pig_detected = True
                name = class_name.lower().replace("_", " ")
                if "pig" in name or "boar" in name:
                    pig_detected = True

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                label = f"{class_name} {conf:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        pig_detected_global = pig_detected
        # if pig_detected:
        #     if esp32:
        #         print("Serial is open:", esp32.is_open)
        #     trigger_deterrent()

        # else:
        #     print("❌ NO DETECTION → sending 0")
        #     stop_deterrent()
        if pig_detected and not prev_detected:

            print("Pig detected -> ON")

            if esp32:
                print("Serial is open:", esp32.is_open)

            trigger_deterrent()

        elif not pig_detected and prev_detected:

            print("Pig gone -> OFF")

            stop_deterrent()

        prev_detected = pig_detected

        # prev_detected = pig_detected

        # UI text
        if pig_detected:
            cv2.putText(frame, "PIG DETECTED - DETERRENT ON",
                        (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 3)

        ret, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video")
def video():
    return Response(generate_frames(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/status")
def status():
    return "Pig Detected" if pig_detected_global else "No Pig Detected"

if __name__ == "__main__":
    app.run(debug=False)
# from flask import Flask, render_template, Response
# from ultralytics import YOLO
# import cv2
# import pygame
# import serial
# import time
# import smtplib
# from email.message import EmailMessage
# import threading

# app = Flask(__name__)

# MODEL_PATH = "best.pt"

# # ESP32-CAM stream URL
# ESP32_CAM_URL = "http://10.50.137.148:81/stream"

# # ESP32-WROOM COM port
# SERIAL_PORT = "COM5"
# BAUD_RATE = 115200

# CONF_THRES = 0.60
# ALERT_COOLDOWN = 30

# SENDER_EMAIL = "11b06sivabalan@gmail.com"
# APP_PASSWORD = "lsek pvnj uhma lezl"
# RECEIVER_EMAIL = "newrajastudio.kpr_bec27@mepcoeng.ac.in"

# model = YOLO(MODEL_PATH)

# last_alert_time = 0
# pig_detected_global = False

# try:
#     esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
#     time.sleep(2)
#     print("ESP32-WROOM connected")
# except:
#     esp32 = None
#     print("ESP32-WROOM not connected")

# pygame.mixer.init()

# def play_predator_sound():
#     try:
#         pygame.mixer.music.load("predator.mp3")
#         pygame.mixer.music.play()
#     except Exception as e:
#         print("Sound error:", e)

# def send_email_alert():
#     try:
#         msg = EmailMessage()
#         msg["Subject"] = "Wild Boar Detected Alert"
#         msg["From"] = SENDER_EMAIL
#         msg["To"] = RECEIVER_EMAIL
#         msg.set_content("Alert: Wild boar/pig detected near the farm. Deterrent system activated.")

#         with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
#             smtp.login(SENDER_EMAIL, APP_PASSWORD)
#             smtp.send_message(msg)

#         print("Email alert sent")

#     except Exception as e:
#         print("Email error:", e)

# def trigger_deterrent():
#     global last_alert_time

#     current_time = time.time()

#     if current_time - last_alert_time > ALERT_COOLDOWN:
#         last_alert_time = current_time

#         if esp32:
#             esp32.write(b'1')

#         threading.Thread(target=play_predator_sound).start()
#         threading.Thread(target=send_email_alert).start()

# def stop_deterrent():
#     if esp32:
#         esp32.write(b'0')
      

# def generate_frames():
#     global pig_detected_global

#     cap = cv2.VideoCapture(ESP32_CAM_URL, cv2.CAP_FFMPEG)

#     if not cap.isOpened():
#         print("Cannot open ESP32-CAM stream")
#         return

#     while True:
#         success, frame = cap.read()

#         if not success:
#             print("Frame not received, reconnecting...")
#             cap.release()
#             time.sleep(1)
#             cap = cv2.VideoCapture(ESP32_CAM_URL, cv2.CAP_FFMPEG)
#             continue

#         results = model(frame, conf=CONF_THRES, verbose=False)

#         pig_detected = False

#         for result in results:
#             for box in result.boxes:
#                 cls_id = int(box.cls[0])
#                 conf = float(box.conf[0])
#                 class_name = model.names[cls_id]

#                 if class_name.lower() in ["pig", "wild boar", "boar"]:
#                     pig_detected = True

#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 label = f"{class_name} {conf:.2f}"

#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                 cv2.putText(frame, label, (x1, y1 - 10),
#                             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

#         pig_detected_global = pig_detected

#         if pig_detected:
#             cv2.putText(frame, "PIG DETECTED - DETERRENT ON",
#                         (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
#                         1, (0, 0, 255), 3)
#             trigger_deterrent()
#         else:
#             stop_deterrent()

#         ret, buffer = cv2.imencode(".jpg", frame)
#         frame = buffer.tobytes()

#         yield (b"--frame\r\n"
#                b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/video")
# def video():
#     return Response(generate_frames(),
#                     mimetype="multipart/x-mixed-replace; boundary=frame")

# @app.route("/status")
# def status():
#     if pig_detected_global:
#         return "Pig Detected"
#     else:
#         return "No Pig Detected"

# if __name__ == "__main__":
#     app.run(debug=False)