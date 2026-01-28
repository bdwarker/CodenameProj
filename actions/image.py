import os
import datetime
import json
import mss
import mss.tools
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

# Load JSON config
with open("config.json", "r") as f:
    config = json.load(f)

# Debug mode flag
DEBUG_MODE = config.get("debug_mode", True)
if DEBUG_MODE:
    print("[~] Debug mode is ON")
    KEEP_SCREENSHOT = True
else:
    KEEP_SCREENSHOT = False



# Load pretrained docTR OCR model
model = ocr_predictor(pretrained=True)

def capture(index:int=1):
    MONITOR_INDEX = config.get("monitor_index", index)
    # Ensure folders exist
    os.makedirs("images", exist_ok=True)

    # Timestamp for filenames
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    image_path = f"images/screenshot_{timestamp}.png"

    # Capture screenshot with MSS
    with mss.mss() as sct:
        monitors = sct.monitors
        if MONITOR_INDEX >= len(monitors):
            raise ValueError(f"Monitor index {MONITOR_INDEX} out of range. Found {len(monitors)-1} monitors.")
        monitor = monitors[MONITOR_INDEX]
        img = sct.grab(monitor)
        mss.tools.to_png(img.rgb, img.size, output=image_path)
    print(f"[+] Screenshot saved: {image_path}")
    return image_path


def capture_and_extract(index:int=1):
    MONITOR_INDEX = config.get("monitor_index", index)
    # Ensure folders exist
    os.makedirs("images", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # Timestamp for filenames
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    image_path = f"images/screenshot_{timestamp}.png"
    text_path = f"outputs/screenshot_{timestamp}.txt"

    # Capture screenshot with MSS
    with mss.mss() as sct:
        monitors = sct.monitors
        if MONITOR_INDEX >= len(monitors):
            raise ValueError(f"Monitor index {MONITOR_INDEX} out of range. Found {len(monitors)-1} monitors.")
        monitor = monitors[MONITOR_INDEX]
        img = sct.grab(monitor)
        mss.tools.to_png(img.rgb, img.size, output=image_path)
    print(f"[+] Screenshot saved: {image_path}")

    # Load image into docTR
    doc = DocumentFile.from_images(image_path)

    # Run OCR
    result = model(doc)

    # Render as plain text
    extracted_text = result.render()

    # Save to text file
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(extracted_text if extracted_text.strip() else "(no text detected)")

    print(f"[+] Extracted text saved to: {text_path}")

    # Delete screenshot if not debugging
    if not KEEP_SCREENSHOT:
        try:
            os.remove(image_path)
            print(f"[+] Screenshot deleted: {image_path}")
        except Exception as e:
            print(f"[!] Could not delete screenshot: {e}")
    else:
        print("[~] Debug mode: Screenshot kept")

    return text_path

if __name__ == "__main__":
    text_file = capture_and_extract()
    with open(text_file, "r", encoding="utf-8") as f:
        extracted_text = f.read()
    print(f"Done. Text available in {text_file}")
