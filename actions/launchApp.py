import pyautogui
import time
import os
def open_app(app_name: str):

    if app_name.lower() == "browser":
        app_name = "firefox"  # or "firefox", "edge", etc. depending on your default browser
        os.system(f"start{app_name}")
    elif app_name.lower() == "spotify":
        app_name = "spotify"
        # Start Spotify directly
        os.system(f"start {app_name}")
        # Play the music
        time.sleep(4)  # wait for Spotify to open
        pyautogui.press("space")
    else:
        # Press Win key
        pyautogui.hotkey('win')
        time.sleep(0.5)  # small delay so search box appears
        
        # Type the app name
        pyautogui.typewrite(app_name)
        time.sleep(0.5)  # wait a bit for search results
        
        # Press Enter
        pyautogui.press('enter')
