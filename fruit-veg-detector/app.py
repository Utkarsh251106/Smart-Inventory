import streamlit as st
import cv2
import tempfile
import numpy as np
import requests
import os
import time
from ultralytics import YOLO

# Load YOLOv11 model
@st.cache_resource
def load_model():
    model_path = os.path.join("..", "models", "best.pt")
    return YOLO(model_path)

model = load_model()

# Define class names
CLASS_NAMES = {
    0: "Cabbage",
    1: "Capsicum",
    2: "orange",
    3: "pineapple",
    4: "tomato",
    5: "watermelon"
}

# Define class-specific colors for bounding boxes
CLASS_COLORS = {
    0: (255, 0, 0),     # Blue for Cabbage
    1: (0, 255, 255),   # Yellow for Capsicum
    2: (0, 165, 255),   # Orange for Orange
    3: (0, 255, 0),     # Green for pineapple
    4: (0, 0, 255),     # Red for Tomato
    5: (255, 0, 255)    # Purple for Watermelon
}

# Function to send Telegram alerts
def send_telegram_alert(message, bot_token, chat_id):
    """Send a Telegram message"""
    if not bot_token or not chat_id:
        st.warning("⚠️ Telegram credentials not provided. Alert not sent.")
        return False
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Failed to send Telegram alert: {str(e)}")
        return False

# Streamlit UI
st.title("🥦🍅 Vegetable Detection and Alert System")
st.write("Upload a video to detect vegetables and receive Telegram alerts when quantities drop.")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Telegram configuration
    st.subheader("Telegram Alerts")
    enable_telegram = st.checkbox("Enable Telegram Alerts", value=False)
    
    bot_token = st.text_input("Bot Token", value=os.getenv("BOT_TOKEN", ""), type="password") if enable_telegram else ""
    chat_id = st.text_input("Chat ID", value=os.getenv("CHAT_ID", "")) if enable_telegram else ""
    
    # Detection settings
    st.subheader("Detection Settings")
    confidence_threshold = st.slider("Confidence Threshold", min_value=0.1, max_value=1.0, value=0.3, step=0.05)
    low_count_threshold = st.slider("Low Count Threshold", min_value=1, max_value=10, value=5, step=1)
    detection_time_seconds = st.slider("Detection Time (seconds)", min_value=1, max_value=10, value=5, step=1)
    alert_time_seconds = st.slider("Alert Time (seconds)", min_value=1, max_value=10, value=5, step=1)

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
    
    # Dictionaries for alert tracking
    detection_start_time = {}  # Tracks how long a category has been detected
    low_count_start_time = {}  # Tracks how long a category is below threshold
    alert_sent = {}  # Prevent multiple alerts

    # Process video
    progress_bar = st.progress(0)
    processed_frames = 0
    
    # Create a placeholder for status messages
    status_msg = st.empty()
    
    # Frame timestamp for alert logic
    frame_timestamp = 0
    frame_time_increment = 1.0 / fps if fps > 0 else 0.033  # Default to ~30fps

    # Alert history for display
    alert_history = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Update frame timestamp (simulate time passage)
        frame_timestamp += frame_time_increment

        # Run YOLOv8 detection
        results = model(frame)

        frame_counts = {}

        for r in results:
            for box in r.boxes:
                class_id = int(box.cls[0])  # Class index
                confidence = float(box.conf[0])  # Confidence score
                if confidence >= confidence_threshold:
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

        # Telegram alert logic - if enabled
        if enable_telegram and bot_token and chat_id:
            # Convert frame_counts (categories) to class_ids for alert logic
            class_id_counts = {}
            for category, count in frame_counts.items():
                for class_id, name in CLASS_NAMES.items():
                    if name == category:
                        class_id_counts[class_id] = count
                        break
            
            # Track detected categories for alerts
            for class_id, count in class_id_counts.items():
                # If category detected for the first time, start tracking
                if class_id not in detection_start_time:
                    detection_start_time[class_id] = frame_timestamp
                    alert_sent[class_id] = False  # Reset alert flag
                
                # If detected for specified seconds, it qualifies for low-count tracking
                elif frame_timestamp - detection_start_time[class_id] >= detection_time_seconds:
                    if count < low_count_threshold:
                        if class_id not in low_count_start_time:
                            low_count_start_time[class_id] = frame_timestamp  # Start tracking low count
                        elif frame_timestamp - low_count_start_time[class_id] >= alert_time_seconds and not alert_sent[class_id]:
                            alert_message = f"⚠️ Low {CLASS_NAMES[class_id]} Alert! Only {count} detected for {alert_time_seconds}+ seconds."
                            
                            # Send alert
                            if send_telegram_alert(alert_message, bot_token, chat_id):
                                alert_sent[class_id] = True  # Mark alert as sent
                                alert_history.append(alert_message)
                                status_msg.info(f"✅ Alert sent: {alert_message}")
                    else:
                        # Reset low count timer if count is back to normal
                        if class_id in low_count_start_time:
                            del low_count_start_time[class_id]
                        alert_sent[class_id] = False  # Reset alert flag

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
    
    # Display alert history if any
    if enable_telegram and alert_history:
        st.subheader("🚨 Alert History")
        for alert in alert_history:
            st.warning(alert)

    # Cleanup temp files
    os.remove(temp_video_path)
    os.remove(output_video_path)