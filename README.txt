# Armor Finder – Static Frontend

This is a standalone, responsive HTML/CSS/JS implementation that matches your GIMP/XCF design and behavior. It is ready to wire to your Flask backend at `POST /process`.

## Files
- `index.html` – semantic markup for layout and sections (Title, File Box, Bars, User Selection, Process button, Output area).
- `styles.css` – modern, accessible styling with CSS variables for the light blue/green states.
- `app.js` – interactivity:
  - Drag & drop + click-to-upload, with **filename** and **500KB** size checks.
  - Toggle cards for **Class (3)**, **Archetype (6)**, **Set (12)** (off = light blue; on = light green).
  - **Process** button color reflects freshness (blue = needs run; green = up-to-date). Changes to file/selections mark it blue.
  - Two output fields with **Copy** buttons that copy the adjacent field.
  - Sends `FormData` with `file`, and JSON arrays: `class`, `archetype`, `set` to `/process`.
  - Expects JSON response `{ resultTop, resultBottom }` (or `{ result }` for a single output).

## Hooking to Flask
Your Flask endpoint should look like:

```python
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.post('/process')
def process():
    f = request.files['file']  # destiny-armor.csv
    classes = json.loads(request.form.get('class', '[]'))
    archetypes = json.loads(request.form.get('archetype', '[]'))
    sets = json.loads(request.form.get('set', '[]'))

    # TODO: Replace with your processing logic
    top = f"Classes: {classes}\nArchetypes: {archetypes}\nSets: {sets}"
    bottom = "Your second output string here"

    return jsonify({"resultTop": top, "resultBottom": bottom})
```

## Customizing Text to Match Your .XCF
- Title: edit the `<h1 id="appTitle">` in `index.html`.
- File box texts: change `#fileBoxTitle`, `#fileBoxSub`, `#fileBoxNote` contents.
- The three bars: change `#classBar`, `#archetypeBar`, `#setBar` text.
- Button labels for the 3/6/12 cards are literal text and can be changed in `index.html`, or injected via JS.

## Colors
The light **blue** and **green** are set in `styles.css` as variables:
```css
--accent-off: #6db6ff; /* blue */
--accent-on:  #69db87; /* green */
```
Adjust to match the exact hues from your GIMP file.

## Running Locally (static preview)
Just open `index.html` in a browser. The page loads and UI works; the **Process** button will try to POST to `/process`. For a full test, run your Flask app at `http://localhost:5000` with that route.

## Notes
- The layout is responsive; grids collapse cleanly on smaller screens.
- All interactive elements are keyboard-accessible and have visual focus states.
- File validation enforces **exact filename** and **max 500KB** per your spec.
