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

ESP32_CAM_URL = "http://10.30.198.148:81/stream"

SERIAL_PORT = "COM5"
BAUD_RATE = 115200

CONF_THRES = 0.75

ALERT_COOLDOWN = 30
DETECTION_HOLD = 0.3

SENDER_EMAIL = "11b06sivabalan@gmail.com"
APP_PASSWORD = "eael ocdp bjej rsjb"
RECEIVER_EMAIL = "newrajastudio.kpr_bec27@mepcoeng.ac.in"

model = YOLO(MODEL_PATH)

last_alert_time = 0
last_seen_time = 0

pig_detected_global = False
alarm_active = False

try:
    esp32 = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("ESP32-WROOM connected")

except Exception as e:
    esp32 = None
    print("ESP32-WROOM not connected")
    print(e)

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

        msg.set_content(
            "Alert: Wild boar detected. Deterrent activated."
        )

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:

            smtp.login(SENDER_EMAIL, APP_PASSWORD)
            smtp.send_message(msg)

        print("Email alert sent")

    except Exception as e:
        print("Email error:", e)


def trigger_deterrent():

    global last_alert_time
    global alarm_active

    if alarm_active:
        return

    alarm_active = True

    if esp32:
        esp32.write(b'1\n')
        esp32.flush()

        print(">>> SENT 1 TO ESP32")

    current_time = time.time()

    if current_time - last_alert_time > ALERT_COOLDOWN:

        last_alert_time = current_time

        threading.Thread(target=play_predator_sound).start()
        threading.Thread(target=send_email_alert).start()


def stop_deterrent():

    global alarm_active

    if not alarm_active:
        return

    alarm_active = False

    if esp32:

        esp32.write(b'0\n')
        esp32.flush()

        print(">>> SENT 0 TO ESP32")


def generate_frames():

    global pig_detected_global
    global last_seen_time

    print("Connecting to ESP32-CAM...")

    cap = cv2.VideoCapture(ESP32_CAM_URL)

    if not cap.isOpened():

        print("Cannot open ESP32-CAM stream")
        return

    print("ESP32-CAM connected")

    while True:

        success, frame = cap.read()

        if not success:

            print("Frame not received, reconnecting...")

            cap.release()

            time.sleep(1)

            cap = cv2.VideoCapture(ESP32_CAM_URL)

            continue

        results = model(frame, conf=CONF_THRES, verbose=False)

        pig_detected = False

        for result in results:

            for box in result.boxes:

                cls_id = int(box.cls[0])

                conf = float(box.conf[0])

                class_name = model.names[cls_id]

                name = class_name.lower().replace("_", " ")

                if "pig" in name or "boar" in name:

                    pig_detected = True

                    last_seen_time = time.time()

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                label = f"{class_name} {conf:.2f}"

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

        pig_detected_global = pig_detected

        current_time = time.time()

        # TURN ON
        if pig_detected and not alarm_active:

            print("Pig detected -> ALARM ON")

            trigger_deterrent()

        # TURN OFF AFTER HOLD TIME
        elif alarm_active and (current_time - last_seen_time > DETECTION_HOLD):

            print("No pig for 3 sec -> ALARM OFF")

            stop_deterrent()

        # UI TEXT
        if alarm_active:

            cv2.putText(
                frame,
                "PIG DETECTED - DETERRENT ON",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3
            )

        ret, buffer = cv2.imencode(".jpg", frame)

        frame = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame +
            b"\r\n"
        )


@app.route("/")
def index():

    return render_template("index.html")


@app.route("/video")
def video():

    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/status")
def status():

    if alarm_active:
        return "Pig Detected"

    return "No Pig Detected"


if __name__ == "__main__":

    app.run(debug=False)