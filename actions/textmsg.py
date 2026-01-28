import pyautogui
import time
import json

with open("database/contacts.json", "r") as f:
    contacts = json.load(f)

# Function to send a text message using a messaging app
def send_text_message(app_name: str, contact_name: str, message: str, send: bool = False):
    contact_name = contact_name.lower()

    if app_name.lower() == "whatsapp":
        if contact_name in contacts:
            contact_number = contacts[contact_name]
        else:
            print(f"Contact {contact_name} not found in contacts database.")
            return
        # Press Win key to open Start menu
        pyautogui.hotkey('win')
        time.sleep(0.5)  # small delay so search box appears

        # Type the app name
        pyautogui.typewrite(app_name)
        time.sleep(0.5)  # wait a bit for search results

        # Press Enter to open the app
        pyautogui.press('enter')
        time.sleep(3)  # wait for the app to open
        # close any current open chat
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(0.5)
        # Search for the contact
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)
        #clear any existing text
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('backspace')
        time.sleep(0.2)
        pyautogui.typewrite(contact_number)
        time.sleep(1)  # wait for search results
        # Press down arrow to select the contact
        pyautogui.press('down')
        time.sleep(0.5)
        pyautogui.press('enter')
        time.sleep(1)  # wait for chat to open
        # Clear draft message if any
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.press('backspace')
        time.sleep(0.2)
        pyautogui.typewrite(message)
        time.sleep(0.5)
        if send:
            pyautogui.press('enter')  # send the message
            print(f"Message sent to {contact_name} via {app_name}.")
        else:
            print(f"Message typed to {contact_name} via {app_name}. Not sent (send=False).")
    elif app_name.lower() == "discord":
        pyautogui.hotkey('win', '3')  # Assuming Discord is pinned to taskbar position 3
        time.sleep(6)  # wait for Discord to open
        pyautogui.hotkey('ctrl', 'k')  # Open quick switcher
        time.sleep(1)
        pyautogui.typewrite(contact_name)  # Type the contact name
        time.sleep(2)  # wait for search results
        pyautogui.press('enter')  # Open the chat
        time.sleep(2)  # wait for chat to open
        pyautogui.typewrite(message)  # Type the message
        time.sleep(0.5)
        if send:
            pyautogui.press('enter')  # send the message
            print(f"Message sent to {contact_name} via {app_name}.")
        else:
            print(f"Message typed to {contact_name} via {app_name}. Not sent (send=False).")

if __name__ == "__main__":
    send_text_message("WhatsApp", "Mummy", "Hello, this is a test message!")