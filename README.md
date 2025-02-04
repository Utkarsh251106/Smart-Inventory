## Description
This project utilizes YOLOv11n for detecting and counting tomatoes in video streams. It processes the video to identify and count the number of tomatoes in each frame, alerting the user via Telegram if the tomato count drops below 5 for more than 5 seconds. The project is designed to handle real-time video input and provide continuous monitoring of the detected object, sending notifications when needed.

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
Follow this path to get the model(best.pt)-> model-training-data/runs/model
#### Run your Code_for_images.ipynb file for image detection
#### Run your Code_for_video.ipynb file for image detection
