#!/bin/bash

echo "🚀 Launching Thesis Calendar GUI"

# Navigate to the project folder (adjust path if needed)
cd ~/Desktop/Projects/Auto_cal || {
  echo "❌ Could not find Auto_cal folder"
  exit 1
}

# Activate virtual environment
source venv/bin/activate

# Run the GUI
python thesis_gui.py