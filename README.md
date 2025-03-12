## Description
This project utilizes YOLOv11n for detecting and counting vegtables and fruits in an image or a video streams. It processes the video to identify and count the number of items in each frame, alerting the user via Telegram if the tomato count drops below 5 for more than 5 seconds. The project is designed to handle real-time video input and provide continuous monitoring of the detected object, sending notifications when needed.

# How to run it?
### Step 1: Clone the Repository:
  
```bash
git clone https://github.com/Utkarsh251106/Smart-Inventory
```
### Step 2: Create a conda environment:
  
```bash
conda create -n venv python=3.12.7 -y
conda activate venv
```

### Step 3: Install the requirements:
  
```bash
pip install -r requirements.txt
```
### Step 4: To run the code:
  To run the code
```bash
# Start the Jupyter Notebook environment using the command
jupyter notebook
```
Follow this path to get the model(best.pt)-> model-training-data/runs/model for tomatoes
#### Run your Code_for_images.ipynb file for detection in an image
#### Run your Code_for_video.ipynb file for detections in a video

Follow this path to get the model(best.pt)-> Fruit-and-Vegetable-detection/runs/detect/train/weights  for vegtables and fruits
#### Run your Code_for_images.ipynb file for detection in an image
#### Run your Code_for_video.ipynb file for detections in a video

### Step 5(Optional): To run the streamlit file(present in the Fruit-and-Vegetable-detection folder):
  To run the code
```bash
# Start the Jupyter Notebook environment using the command
streamlit run app.py
```