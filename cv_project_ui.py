#!/usr/bin/env python3
"""
Computer Vision Project - Main UI
Welcome to Having Fun with Computer Vision
"""

import streamlit as st
import subprocess
import sys
import os
from pathlib import Path
import threading
import time

# ---------------------------
# Project Root - Update this path to match your actual project location
# ---------------------------
PROJECT_ROOT = Path(__file__).resolve().parent


# ---------------------------
# Streamlit Page Config
# ---------------------------
st.set_page_config(
    page_title="Having Fun with Computer Vision",
    page_icon="🎮",
    layout="wide"
)

# ---------------------------
# Custom CSS
# ---------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 3em;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .feature-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #1E88E5;
    }
    .feature-title {
        font-size: 1.5em;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        font-size: 1em;
        color: #555;
        margin-bottom: 1rem;
    }
    .loading-box {
        background-color: #e3f2fd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2196F3;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #ffebee;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #f44336;
        margin: 1rem 0;
    }
    .info-text {
        font-size: 1.1em;
        color: #2196F3;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Header
# ---------------------------
st.markdown('<div class="main-header">🎮 Welcome to Having Fun with Computer Vision</div>', unsafe_allow_html=True)

# ---------------------------
# Sidebar Navigation
# ---------------------------
st.sidebar.title("📋 Navigation")
feature = st.sidebar.selectbox(
    "Select a Feature to Run:",
    [
        "Select a feature...",
        "Emotion Detection",
        "Hand Tracking",
        "Virtual Games",
        "Volume Gesture Control",
        "YOLO Tracking"
    ]
)

# ---------------------------
# Helper function to run scripts with better process management
# ---------------------------
def run_script(relative_path, script_name):
    script_path = PROJECT_ROOT / relative_path
    
    if not script_path.exists():
        st.error(f"❌ Script not found: {script_path}")
        return False
    
    st.markdown(f'<div class="loading-box"><div class="info-text">🚀 Launching {script_name}...</div><div style="font-size: 0.9em; color: #666;">This may take a few seconds. Please wait...</div></div>', unsafe_allow_html=True)
    
    try:
        # Run script in a separate process and wait for it to complete
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Wait for the process to complete (this keeps the UI responsive)
        stdout, stderr = process.communicate(timeout=30)  # 30 second timeout
        
        if process.returncode == 0:
            st.markdown(f'<div class="success-box"><div class="info-text">✅ {script_name} completed successfully!</div></div>', unsafe_allow_html=True)
            return True
        else:
            st.markdown(f'<div class="error-box"><div class="info-text">❌ {script_name} failed!</div><div style="font-size: 0.9em; color: #f44336;">Error: {stderr}</div></div>', unsafe_allow_html=True)
            return False
            
    except subprocess.TimeoutExpired:
        st.markdown(f'<div class="success-box"><div class="info-text">✅ {script_name} launched successfully!</div><div style="font-size: 0.9em; color: #4CAF50;">The application is now running in the background.</div></div>', unsafe_allow_html=True)
        return True
    except Exception as e:
        st.markdown(f'<div class="error-box"><div class="info-text">❌ Failed to run {script_name}!</div><div style="font-size: 0.9em; color: #f44336;">Error: {str(e)}</div></div>', unsafe_allow_html=True)
        return False

# ---------------------------
# Features
# ---------------------------
if feature == "Select a feature...":
    st.markdown("""
    ## 🎯 Choose a Feature from the Sidebar
    
    Explore the exciting world of computer vision with these interactive features:
    
    ### 📊 Features Available:
    
    **Emotion Detection** - Detect emotions from your webcam feed using deep learning models.
    
    **Hand Tracking** - Track hand gestures including finger counting and thumb direction.
    
    **Virtual Games** - Interactive games using computer vision:
    - Guessing Game - Solve riddles using a virtual keyboard
    - Psychology Game - Answer questions with hand gestures to discover your personality type
    - Tic-Tac-Toe - Play against the computer using virtual drawing
    
    **Volume Gesture Control** - Control your laptop volume with hand gestures.
    
    **YOLO Tracking** - Real-time object detection and tracking using YOLOv8.
    """)
    
    # Display cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""<div class="feature-card"><div class="feature-title">😊 Emotion Detection</div><div class="feature-desc">Detect facial emotions in real-time</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="feature-card"><div class="feature-title">✋ Hand Tracking</div><div class="feature-desc">Count fingers and track thumb gestures</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class="feature-card"><div class="feature-title">🎮 Virtual Games</div><div class="feature-desc">Interactive games with gesture control</div></div>""", unsafe_allow_html=True)

# ---------------------------
# Emotion Detection
# ---------------------------
elif feature == "Emotion Detection":
    st.markdown("""<div class='feature-card'><div class='feature-title'>😊 Emotion Detection</div><div class='feature-desc'>Uses a trained model to detect facial emotions in real-time.</div></div>""", unsafe_allow_html=True)
    if st.button("🚀 Start Emotion Detection"):
        run_script("Emotion_detection/tes.py", "Emotion Detection")

# ---------------------------
# Hand Tracking
# ---------------------------
elif feature == "Hand Tracking":
    st.markdown("""<div class='feature-card'><div class='feature-title'>✋ Hand Tracking</div><div class='feature-desc'>Counts fingers and detects thumbs up/down gestures in real-time.</div></div>""", unsafe_allow_html=True)
    if st.button("🚀 Start Hand Tracking"):
        run_script("pose_detection/hand_tracking.py", "Hand Tracking")

# ---------------------------
# Virtual Games
# ---------------------------
elif feature == "Virtual Games":
    st.markdown("""<div class='feature-card'><div class='feature-title'>🎮 Virtual Games</div><div class='feature-desc'>Select a game to play using computer vision gestures.</div></div>""", unsafe_allow_html=True)
    
    game_choice = st.selectbox("Select a Game:", ["Select a game...", "Guessing Game", "Psychology Game", "Tic-Tac-Toe"])
    
    if game_choice == "Guessing Game" and st.button("🚀 Start Guessing Game"):
        run_script("virtuals/guessing_game.py", "Guessing Game")
    
    elif game_choice == "Psychology Game" and st.button("🚀 Start Psychology Game"):
        run_script("virtuals/physcology_test.py", "Psychology Game")
    
    elif game_choice == "Tic-Tac-Toe" and st.button("🚀 Start Tic-Tac-Toe"):
        run_script("virtuals/Tic_tac_toe.py", "Tic-Tac-Toe")

# ---------------------------
# Volume Gesture Control
# ---------------------------
elif feature == "Volume Gesture Control":
    st.markdown("""<div class='feature-card'><div class='feature-title'>🔊 Volume Gesture Control</div><div class='feature-desc'>Control your laptop's volume with hand gestures.</div></div>""", unsafe_allow_html=True)
    if st.button("🚀 Start Volume Control"):
        run_script("virtuals/Volume gesture control.py", "Volume Control")

# ---------------------------
# YOLO Tracking
# ---------------------------
elif feature == "YOLO Tracking":
    st.markdown("""<div class='feature-card'><div class='feature-title'>🔍 YOLO Tracking</div><div class='feature-desc'>Real-time object detection and tracking using YOLOv8.</div></div>""", unsafe_allow_html=True)
    if st.button("🚀 Start YOLO Tracking"):
        run_script("yolo webcam detection/Tracking.py", "YOLO Tracking")

# ---------------------------
# Footer
# ---------------------------
st.markdown("<hr><div style='text-align:center;color:#666;'>🎮 Having Fun with Computer Vision - Built with Streamlit & OpenCV</div>", unsafe_allow_html=True)
