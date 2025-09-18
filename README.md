# Rock-Paper-Scissors Game

A simple and interactive Rock-Paper-Scissors game built with Python. Play against the computer, enjoy a graphical interface, and have fun!

## Features

- User-friendly GUI for easy gameplay
- Real-time score tracking
- Visual representation of choices (Rock, Paper, Scissors images)
- Video or animation support for enhanced experience

## Getting Started

### Prerequisites

- Python 3.8–3.12 (Because Mediapipe does not support Python 3.13+ as of September 2025)
- Required libraries: `mediapipe`,`opencv-python`

### Installation

1. Clone this repository or download the source code.
2. Ensure all image files (`Rock.png`, `Paper.png`, `Scissors.png`) and `playing_video.mp4` are in the project directory.
3. Install dependencies:
	```powershell
	pip install -r requirements.txt
	```

### Running the App

Run the following command in your terminal:
```powershell
python app.py
```

## Usage

- Select your choice: Rock, Paper, or Scissors.
- The computer will randomly select its choice.
- The winner is displayed, and scores are updated.

## File Structure

- `app.py` — Main application file
- `Assets/` -> `Rock.png`, `Paper.png`, `Scissors.png`, `playing_video.mp4` — Images for choices & video for animation
- `README.md` — Project documentation
- `requirements.txt` — Module requirements
- `rock-paper-scissors.task` — ML model


