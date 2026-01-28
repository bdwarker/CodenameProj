import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import json
import warnings
from dotenv import load_dotenv
from PIL import Image

# Suppress noisy warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=FutureWarning, module="TTS.utils.io")
warnings.filterwarnings("ignore", category=FutureWarning, module="doctr.models.utils.pytorch")

# Assistant imports
from utils.elevenlabsAPI import playFinale
from utils.tts import ttsRun, stop_audio
from utils.memory import add_memory, clear_memory
from utils.log import log_to_file
from utils.speechRecog import speech_to_text, stop_listening
from actions.actions import *
from actions.actions import *
from actions.brain import ollamaReply, ollamaJson, ollamaSeeImage, ollamaGenerateContent
from actions.image import capture_and_extract
from utils.config_manager import load_config, save_config, get_config_value, set_config_value

# Load config
load_dotenv()
config = load_config()
OLLAMA_MODEL = config.get("ollama_model", "gemma3:4b")
assistant_name = config.get("name", "Assistant")

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class AssistantGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{assistant_name}")
        self.geometry("900x600")

        self.running = True
        self.speech_thread = None
        self.current_status = "Idle"

        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text=f"{assistant_name}", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_chat = ctk.CTkButton(self.sidebar_frame, text="Chat", command=self.show_chat_frame)
        self.sidebar_button_chat.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_settings = ctk.CTkButton(self.sidebar_frame, text="Settings", command=self.show_settings_frame)
        self.sidebar_button_settings.grid(row=2, column=0, padx=20, pady=10)

        self.clear_memory_btn = ctk.CTkButton(self.sidebar_frame, text="Clear Memory", command=self.clear_memory_action, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.clear_memory_btn.grid(row=5, column=0, padx=20, pady=10)
        
        self.clear_logs_btn = ctk.CTkButton(self.sidebar_frame, text="Clear Logs", command=self.clear_logs_action, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.clear_logs_btn.grid(row=6, column=0, padx=20, pady=(10, 20))

        # Main Chat Frame
        self.chat_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(0, weight=1)

        self.chat_display = ctk.CTkTextbox(self.chat_frame, width=250, state="disabled")
        self.chat_display.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.entry_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.entry_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
        self.entry_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.entry_frame, placeholder_text="Type a message...")
        self.entry.grid(row=0, column=0, padx=(0, 20), pady=0, sticky="ew")
        self.entry.bind("<Return>", self.send_message_event)

        self.send_btn = ctk.CTkButton(self.entry_frame, text="Send", width=100, command=self.send_message)
        self.send_btn.grid(row=0, column=1, padx=(0, 10))
        
        self.mic_btn = ctk.CTkButton(self.entry_frame, text="🎤", width=40, command=self.toggle_speech_mode)
        self.mic_btn.grid(row=0, column=2, padx=(0, 10))

        self.stop_btn = ctk.CTkButton(self.entry_frame, text="Stop", width=60, fg_color="#FF5555", hover_color="#CC0000", command=self.stop_action)
        self.stop_btn.grid(row=0, column=3)

        # Status Bar
        self.status_label = ctk.CTkLabel(self.chat_frame, text="Status: Idle", font=ctk.CTkFont(size=12), text_color="gray")
        self.status_label.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="w")

        # Settings Frame
        self.settings_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.settings_frame.grid_columnconfigure(0, weight=1)

        self.settings_label = ctk.CTkLabel(self.settings_frame, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        self.settings_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.name_label = ctk.CTkLabel(self.settings_frame, text="Assistant Name:")
        self.name_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.name_entry = ctk.CTkEntry(self.settings_frame, width=300)
        self.name_entry.insert(0, assistant_name)
        self.name_entry.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="w")

        self.model_label = ctk.CTkLabel(self.settings_frame, text="Ollama Model:")
        self.model_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.model_entry = ctk.CTkEntry(self.settings_frame, width=300)
        self.model_entry.insert(0, OLLAMA_MODEL)
        self.model_entry.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="w")

        self.save_settings_btn = ctk.CTkButton(self.settings_frame, text="Save Settings", command=self.save_settings)
        self.save_settings_btn.grid(row=5, column=0, padx=20, pady=20, sticky="w")

        # Initial View
        self.show_chat_frame()
        self.display_message(f"{assistant_name}", f"Hello! {assistant_name} at your service. How can I assist you today?")
        
        # Speech Mode State
        self.speech_mode = False

    def show_chat_frame(self):
        self.settings_frame.grid_forget()
        self.chat_frame.grid(row=0, column=1, sticky="nsew")

    def show_settings_frame(self):
        self.chat_frame.grid_forget()
        self.settings_frame.grid(row=0, column=1, sticky="nsew")

    def update_status(self, status):
        self.current_status = status
        self.status_label.configure(text=f"Status: {status}")
        if status == "Listening":
            self.status_label.configure(text_color="#55FF55") # Green
        elif status == "Thinking":
            self.status_label.configure(text_color="#FFFF55") # Yellow
        elif status == "Speaking":
            self.status_label.configure(text_color="#5555FF") # Blue
        else:
            self.status_label.configure(text_color="gray")

    def send_message_event(self, event):
        self.send_message()

    def send_message(self):
        user_input = self.entry.get().strip()
        if not user_input:
            return
        self.entry.delete(0, tk.END)
        self.handle_input(user_input)

    def toggle_speech_mode(self):
        if self.speech_mode:
            self.speech_mode = False
            self.mic_btn.configure(fg_color=["#3B8ED0", "#1F6AA5"]) # Default blue
            stop_listening()
            self.update_status("Idle")
        else:
            self.speech_mode = True
            self.mic_btn.configure(fg_color="#FF5555") # Red to indicate active
            if not self.speech_thread or not self.speech_thread.is_alive():
                self.speech_thread = threading.Thread(target=self.continuous_listen, daemon=True)
                self.speech_thread.start()

    def stop_action(self):
        """Interrupts current action (TTS or listening)."""
        stop_audio()
        stop_listening()
        self.update_status("Interrupted")
        # If in speech mode, we might want to restart listening after a short pause or just go to idle
        if self.speech_mode:
             # For simplicity, let's keep speech mode active but reset status
             self.after(1000, lambda: self.update_status("Listening") if self.speech_mode else None)

    def continuous_listen(self):
        """Keeps listening until mode is switched back or program stops."""
        while self.running and self.speech_mode:
            try:
                self.update_status("Listening")
                user_input = speech_to_text()
                if not self.running or not self.speech_mode:
                    break
                if user_input:
                    # Process inline so it blocks until Assistant finishes replying
                    self.handle_input_sync(user_input)
            except Exception as e:
                # print(f"Speech error: {e}")
                # self.speech_mode = False
                # self.mic_btn.configure(fg_color=["#3B8ED0", "#1F6AA5"])
                # self.update_status("Error")
                pass

    def handle_input(self, user_input):
        self.display_message("You", user_input)
        log_to_file("user_input", user_input)
        threading.Thread(target=self.process_actions, args=(user_input,), daemon=True).start()

    def handle_input_sync(self, user_input):
        """Blocking version for speech mode — wait until reply finishes before looping."""
        self.display_message("You", user_input)
        log_to_file("user_input", user_input)
        self.process_actions(user_input)

    def process_actions(self, user_input):
        self.update_status("Thinking")
        try:
            output = ollamaJson(user_input)
            if not isinstance(output, list):
                output = [output]

            for act in output:
                if not self.running: break # Stop processing if app closed

                action = act.get("action")
                if action == "open_browser":
                    open_browser()
                elif action == "launch_app":
                    launch(act["details"])
                elif action == "search_browser":
                    search(act["details"])
                elif action == "clear logs":
                    self.clear_logs_action()
                elif action == "clear memory":
                    self.clear_memory_action()
                elif action == "reply" and not act.get("remember", False):
                    reply = ollamaReply(user_input)
                    self.reply(reply, reply)
                elif action == "open_link":
                    url = act.get("details")
                    if url:
                        open_link(url)
                    else:
                        self.reply("❓ No link provided.", "I'm sorry, no link was provided.")
                elif action == "remember" and act.get("remember", False):
                    rememberReply = ollamaReply("You can remember things. " + user_input)
                    add_memory(act.get("memory_key", "general"), act.get("memory_value", user_input))
                    self.reply("🧠 Memory added", rememberReply)
                    self.reply(f"🗣️ I've remembered that {act.get('memory_key', 'general')}", f"I've remembered that {act.get('memory_key', 'general')}")
                elif action == "see_screen":
                    if not act["details"].isdigit() or int(act["details"]) < 1:
                        self.reply("❓ Invalid monitor index.", "The monitor index should be an integer.")
                    else:
                        index = int(act["details"])
                        text_file = capture_and_extract(index)
                        with open(text_file, "r", encoding="utf-8") as f:
                            extracted_text = f.read()
                        screenSummary = ollamaSeeImage(extracted_text, user_input)
                        self.reply("📸 Processed screen", "I've processed the content on the screen. Please wait while I tend to your request.")
                        self.reply(screenSummary, screenSummary)
                elif act["action"] == "type":
                    type_text(act["details"])
                    self.reply(f"⌨️ Typed text: {act['details']}", "Typing the text")
                elif act["action"] == "press_key":
                    press_key(act["details"])
                    self.reply(f"⌨️ Pressed key: {act['details']}", f"Pressed the {act['details']} key")
                elif act["action"] == "read_file":
                    content = read_file(act["details"])
                    self.reply(f"📄 Read file: {act['details']}", f"I've read the file {act['details']}. The content is: {content[:100]}...") # Speak only first 100 chars
                    self.display_message("System", f"Content of {act['details']}:\n{content}")
                elif act["action"] == "write_file":
                    # details might need to be parsed if it contains both path and content. 
                    # For now, assuming details is a JSON string or we need a better way to pass two args.
                    # Let's assume details is "path|content" or similar if the LLM can handle it, 
                    # OR we rely on the LLM to output a specific format.
                    # Actually, the current ollamaJson structure only has "details". 
                    # We might need to update brain.py to handle multiple fields or parse "details".
                    # For simplicity, let's assume details is the path, and we ask the user for content? 
                    # No, that breaks the flow.
                    # Let's assume the LLM puts "path|content" in details.
                    if "|" in act["details"]:
                        path, content = act["details"].split("|", 1)
                        result = write_file(path.strip(), content.strip())
                        self.reply(result, result)
                    else:
                        # Fallback: Check if content is separated by newline instead of pipe
                        details = act["details"]
                        path = details.split('\n')[0].strip()
                        
                        if len(details) > len(path) + 5: # If there's significant content after the path
                             # Assume the rest is content
                             content = details[len(path):].strip()
                             result = write_file(path, content)
                             self.reply(result, result)
                        else:
                            # If no content provided, generate it
                            self.reply(f"Generating content for {path}...", "Generating content, please wait.")
                            generated_content = ollamaGenerateContent(f"Generate content for the file: {path}. User request context: {user_input}")
                            result = write_file(path, generated_content)
                            self.reply(result, f"I've generated and written content to {path}.")
                            self.display_message("System", f"Generated Content for {path}:\n{generated_content}")
                elif act["action"] == "list_dir":
                    result = list_dir(act["details"])
                    self.reply(f"📂 Directory listing: {act['details']}", f"Here are the files in {act['details']}: {result}")
                    self.display_message("System", f"Files in {act['details']}:\n{result}")
                elif act["action"] == "delete_file":
                    result = delete_file(act["details"])
                    self.reply(result, result)
                else:
                    self.reply("❓ Unknown action or invalid format.", "I'm sorry, I didn't understand that action.")

            log_to_file("assistant_output", str(output))
            
        except Exception as e:
            self.reply("❌ Error occurred", str(e))
        
        if self.speech_mode:
             self.update_status("Listening")
        else:
             self.update_status("Idle")

    def reply(self, display_text, speak_text):
        self.display_message(f"{assistant_name}", display_text)
        self.update_status("Speaking")
        ttsRun(speak_text)

    def display_message(self, sender, message):
        self.chat_display.configure(state="normal")
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see(tk.END)

    def clear_memory_action(self):
        clear_memory()
        self.reply("🗑️ Cleared memory", "Cleared memory")

    def clear_logs_action(self):
        for file in LOG_DIR.glob("*.txt"):
            file.unlink()
        self.reply("🗑️ Cleared logs", "Cleared logs")

    def save_settings(self):
        new_name = self.name_entry.get().strip()
        new_model = self.model_entry.get().strip()
        
        if new_name:
            set_config_value("name", new_name)
            global assistant_name
            assistant_name = new_name
            self.title(f"{assistant_name}")
            self.logo_label.configure(text=f"{assistant_name}")
        
        if new_model:
            set_config_value("ollama_model", new_model)
            global OLLAMA_MODEL
            OLLAMA_MODEL = new_model
            
        messagebox.showinfo("Settings Saved", "Settings have been saved. Some changes may require a restart.")

if __name__ == "__main__":
    app = AssistantGUI()
    app.mainloop()
