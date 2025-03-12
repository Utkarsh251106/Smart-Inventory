import streamlit as st
import cv2
import tempfile
import numpy as np
import requests
import os
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("runs/detect/train/weights/best.pt")

# Define class names
CLASS_NAMES = {
    0: "Cabbage",
    1: "Capsicum",
    2: "Orange",
    3: "Tomato",
    4: "Watermelon"
}

# Define class-specific colors for bounding boxes
CLASS_COLORS = {
    0: (255, 0, 0),   # Blue for Cabbage
    1: (0, 255, 255), # Yellow for Capsicum
    2: (0, 165, 255), # Orange for Orange
    3: (0, 255, 0),   # Green for Tomato
    4: (0, 0, 255)    # Red for Watermelon
}

# Streamlit UI
st.title("🥦🍅 Vegetable Detection and Alert System")
st.write("Upload a video to detect vegetables and receive Telegram alerts when quantities drop.")

# File uploader
uploaded_file = st.file_uploader("Upload a video", type=["mp4", "mkv", "webm"])

if uploaded_file is not None:
    # Save uploaded file temporarily
    temp_video_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.read())

    # Load video
    cap = cv2.VideoCapture(temp_video_path)

    # Get video properties
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    # Output video path
    output_video_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    # Dictionary to track detected categories and their quantities
    detected_counts = {}

    # Process video
    progress_bar = st.progress(0)
    processed_frames = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLOv8 detection
        results = model(frame)

        frame_counts = {}

        for r in results:
            for box in r.boxes:
                class_id = int(box.cls[0])  # Class index
                confidence = float(box.conf[0])  # Confidence score
                if confidence >= 0.3:  # Only consider high-confidence detections
                    category = CLASS_NAMES.get(class_id, "Unknown")
                    frame_counts[category] = frame_counts.get(category, 0) + 1
                    detected_counts[category] = detected_counts.get(category, 0) + 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    color = CLASS_COLORS.get(class_id, (255, 255, 255))  # Default to white if unknown

                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{category}", (x1, y1 - 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Display detected categories and counts in the top left corner
        y_offset = 30
        for category, count in frame_counts.items():
            cv2.putText(frame, f"{category}: {count}", (10, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            y_offset += 30

        # Save frame to video
        out.write(frame)

        # Update progress bar
        processed_frames += 1
        progress_bar.progress(processed_frames / frame_count)

    # Release resources
    cap.release()
    out.release()

    # Display download button for processed video
    st.success("✅ Video processing complete! Download your processed video below.")
    with open(output_video_path, "rb") as file:
        st.download_button(label="📥 Download Processed Video", data=file, file_name="processed_video.mp4", mime="video/mp4")

    # Display detected categories
    st.subheader("📋 Detected Categories")
    if detected_counts:
        for category in detected_counts.keys():
            st.write(f"- {category}")
    else:
        st.write("No categories detected.")

    # Cleanup temp files
    os.remove(temp_video_path)