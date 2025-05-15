# Project 300

A gamified Android mobile app built with Python (Kivy) for tracking skills/tasks across three swipable pages.

## Features
- Three horizontally swipable pages, each with a customizable title
- Each page has a 3x4 grid:
  - First column: Editable task/skill name
  - Next three columns: Level 1, 2, 3 (slider 0-100)
  - Star appears when a level reaches 100
  - When all three levels in a row reach 100, the row is cleared and rows below shift up
- Brownish-orange background, clean and gamified UI

## How to Run
1. Install requirements:
   ```
   pip install -r requirements.txt
   ```
2. Add a `star.png` image to the `project_300` folder for the star icon.
3. Run the app:
   ```
   python main.py
   ```

## Notes
- Designed for mobile, but can be run on desktop for testing.
- You can enhance the design, add animations, or persistent storage as needed. 