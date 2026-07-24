# AI-Based-Wild-Animal-Detection-System
Real-time AI-powered wild animal detection and deterrent system using YOLOv8, PyTorch, OpenCV, Flask, and ESP32.

AI-Based Wild Animal Detection and Deterrent System
Overview

This project presents an AI-powered real-time wildlife monitoring system designed to detect wild animals entering agricultural fields and automatically activate deterrent mechanisms.

The system uses YOLOv8 for object detection and integrates ESP32 hardware to trigger alarms when a wild animal is detected.

Features
  Real-time wild animal detection
  Custom-trained YOLOv8 model
  Live camera streaming
  ESP32 integration
  Automatic buzzer activation
  LED warning system
  TensorFlow Lite model conversion
  Flask-based web application

Technologies Used
  Python
  PyTorch
  YOLOv8
  OpenCV
  Flask
  TensorFlow Lite
  ESP32


System Architecture

ESP32-CAM
     ↓
Flask Server
     ↓
YOLOv8 Detection
     ↓
Detection Result
     ↓
ESP32 Controller
     ↓
Buzzer + LED Alert

Dataset
   Custom annotated dataset
   2400+ images
   Roboflow annotation
   Data augmentation
   Train/Validation split


Installation
git clone https://github.com/SIVAkpr/AI-Based-Wild-Animal-Detection-System.git

Install dependencies

pip install -r requirements.txt

Run

python app.py
Future Improvements
Mobile App Notification
Cloud Deployment
Solar Powered System
Edge AI Optimization

Author

Sivabalan R
