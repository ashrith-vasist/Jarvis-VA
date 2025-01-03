import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import subprocess
import requests
import ctypes
import logging
from typing import Optional
import json
import google.generativeai as genai
from pathlib import Path
import tkinter as tk
from tkinter import ttk, font
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import json
from datetime import datetime
import re
from youtubesearchpython import VideosSearch
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import psutil
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key="api_key")

# Spotify API credentials
CLIENT_ID = "Client-id"  # Replace with your Spotify app's Client ID
CLIENT_SECRET = "client-secret"  # Replace with your Spotify app's Client Secret
REDIRECT_URI = "http://localhost:8888/callback/"  # Redirect URI you set in your Spotify app



# Gemini configuration
GENERATION_CONFIG = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

SAFETY_SETTINGS = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
    },
]

class VoiceAssistant:
    def __init__(self):
        """Initialize the voice assistant with necessary components."""
        self.recognizer = sr.Recognizer()
        self.tts_engine = self._initialize_tts()
        self.chat_model = self._initialize_chat_model()
        self.search_directories = self._get_search_directories()
        self.config_file = "assistant_config.json"
        self.admin_passphrase = self._load_admin_passphrase()
        self.spotify = self._initialize_spotify()
        self.is_admin_mode = False
        self.spotify_running = False
        self.gui = None

    def set_gui(self, gui):
        self.gui = gui

    def get_confirmation(self) -> bool:
        """Get confirmation from the user."""
        self.speak("Please say yes or no clearly")
        with sr.Microphone() as source:
            try:
                logger.info("Listening for confirmation...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                command = self.recognizer.recognize_google(audio).lower()
                logger.info(f"Confirmation response: {command}")
                
                affirmative_responses = ["yes", "yeah", "yep", "sure", "okay", "ok"]
                return any(response in command for response in affirmative_responses)
                
            except Exception as e:
                logger.error(f"Error during confirmation: {e}")
                self.speak("I didn't understand your response. Please try again.")
                return False

    def _load_admin_passphrase(self) -> str:
        """Load admin passphrase from config file or create new one."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('admin_passphrase', '')
            return ''
        except Exception as e:
            logger.error(f"Error loading admin passphrase: {e}")
            return ''

    def save_admin_passphrase(self, passphrase: str) -> None:
        """Save admin passphrase to config file."""
        try:
            config = {'admin_passphrase': passphrase}
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            logger.info("Admin passphrase saved successfully")
        except Exception as e:
            logger.error(f"Error saving admin passphrase: {e}")
            self.speak("Failed to save admin passphrase")

    def setup_admin_passphrase(self) -> None:
        """Set up admin passphrase through voice input with improved confirmation."""
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                self.speak("Please say your desired admin passphrase")
                passphrase = self.listen()
                
                if not passphrase:
                    self.speak("I couldn't hear the passphrase. Let's try again.")
                    attempt += 1
                    continue

                self.speak(f"I heard: {passphrase}. Is this correct?")
                
                if self.get_confirmation():
                    self.save_admin_passphrase(passphrase)
                    self.speak("Admin passphrase has been set successfully")
                    return
                
                attempt += 1
                
            except Exception as e:
                logger.error(f"Error in setup_admin_passphrase: {e}")
                attempt += 1

        self.speak("Maximum attempts reached. Please try setting up the passphrase later.")

    def authenticate_admin(self) -> bool:
        """Authenticate user as admin using voice passphrase."""
        if not self.admin_passphrase:
            self.speak("No admin passphrase is set. Would you like to set one now?")
            if self.get_confirmation():
                self.setup_admin_passphrase()
            return False

        self.speak("Please say the admin passphrase")
        passphrase = self.listen()
        
        if not passphrase:
            self.speak("Failed to capture passphrase")
            return False

        is_authenticated = passphrase.lower().strip() == self.admin_passphrase.lower().strip()
        self.speak("Admin access granted" if is_authenticated else "Invalid passphrase")
        return is_authenticated


    def _initialize_tts(self) -> pyttsx3.Engine:
        """Initialize and configure text-to-speech engine."""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            if voices:
                engine.setProperty('voice', voices[1].id)  # Female voice
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1)
            return engine
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            raise

    def _initialize_chat_model(self):
        """Initialize the Gemini chat model."""
        return genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            safety_settings=SAFETY_SETTINGS,
            generation_config=GENERATION_CONFIG,
            system_instruction="""
            Give detailed information about the mentioned topic in 5 sentences 
            """
        )

    def _get_search_directories(self) -> list:
        """Get list of directories to search for applications."""
        username = os.getlogin()
        return [
            Path("C:/Program Files"),
            Path("C:/Program Files (x86)"),
            Path("C:/Windows/System32"),
            Path("C:/Users/Public/Desktop"),
            Path(f"C:/Users/{username}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs"),
            Path("D:/"),
            Path("E:/")
        ]

    def speak(self, text: str) -> None:
        """Convert text to speech."""
        try:
            logger.info(f"Speaking: {text}")
            if self.gui:
                self.gui.add_message(text, is_user = False)
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS error: {e}")
            print(f"Failed to speak: {text}")

    def listen(self) -> str:
        """Listen for voice input and convert to text."""
        with sr.Microphone() as source:
            try:
                if self.gui:
                    self.gui.set_listening_state(True)
                logger.info("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=10)
                command = self.recognizer.recognize_google(audio)
                if self.gui:
                    self.gui.add_message(command, is_user=True)
                    self.gui.set_listening_state(False)
                logger.info(f"User said: {command}")
                return command.lower()
            except Exception as e:
                logger.error(f"Error in listen(): {e}")
                self.speak("I didn't catch that. Could you please repeat?")
                if self.gui:
                    self.gui.set_listening_state(False)
            return ""

    def search_app(self, app_name: str) -> Optional[str]:
        """Search for application in common directories."""
        app_aliases = {
            "word": "winword",
            "excel": "excel",
            "powerpoint": "powerpnt"
        }
        
        search_name = app_aliases.get(app_name.lower(), app_name)
        
        for directory in self.search_directories:
            if not directory.exists():
                continue
                
            try:
                for path in directory.rglob("*"):
                    if path.is_file() and search_name.lower() in path.name.lower() and path.suffix.lower() in ('.exe', '.lnk'):
                        return str(path)
            except Exception as e:
                logger.error(f"Error searching in {directory}: {e}")
        
        return None

    def search_app(self, app_name: str) -> Optional[Path]:
        """Search for application in common directories."""
        if app_name == "word":
            app_name = "winword"
        elif app_name == "excel":
            app_name = "excel"
        elif app_name == "powerpoint":
            app_name = "powerpnt"
        
        
        search_dirs = [
            "C:/Program Files",
            "C:/Program Files (x86)",
            "C:/Windows/System32",
            "C:/Users/Public/Desktop",
            f"C:/Users/{os.getlogin()}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs"
        ]
        
        for directory in search_dirs:
            if not os.path.exists(directory):
                continue
                
            try:
                for root, _, files in os.walk(directory):
                    for file in files:
                        if app_name.lower() in file.lower() and file.endswith(('.exe', '.lnk')):
                            return os.path.join(root, file)
            except PermissionError:
                logger.warning(f"Permission denied accessing {directory}")
            except Exception as e:
                logger.error(f"Error searching in {directory}: {e}")
        
        return None

    def search_folder(self, folder_name: str) -> Optional[Path]:
        """Search for a folder in specified drives.
        Returns the path if found, None otherwise."""

        search_dirs = ["D:\\", "E:\\"]

        try:
            for directory in search_dirs:
                if not os.path.exists(directory):
                    logger.warning(f"Drive {directory} is not accessible")
                    continue

                logger.info(f"Searching in {directory}")
                for root, dirs, _ in os.walk(directory):
                    for dir_name in dirs:
                        if folder_name.lower() in dir_name.lower():
                            full_path = os.path.join(root, dir_name)
                            logger.info(f"Found folder: {full_path}")
                            return str(full_path)

        except PermissionError:
            logger.warning("Permission denied while accessing some directories")
        except Exception as e:
            logger.error(f"Error searching folders: {e}")

        return None

    def open_folder(self, folder_name: str) -> None:
        """
        Open a folder in the default file explorer.
        :param folder_name: The name of the folder to open.
        """
        
        try:
            path = self.search_folder(folder_name)
            print(path)
            if path:
                self.speak(f"Opening folder {folder_name}")
                os.startfile(path)
            else:
                self.speak(f"Could not find folder {folder_name}")
        except Exception as e:
            logger.error(f"Error opening folder: {e}")
            self.speak(f"Error opening folder {folder_name}")


    def open_application(self, app_name: str) -> None:
        """Open an application with proper error handling."""
        path = self.search_app(app_name)
        if not path:
            self.speak(f"Application {app_name} not found.")
            return

        try:
            self.speak(f"Opening {app_name}")
            if path.endswith('.lnk'):
                os.startfile(path)
            else:
                subprocess.run([path], check=True)
        except PermissionError:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                try:
                    self.speak(f"Attempting to open {app_name} with administrator privileges.")
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", path, None, None, 1)
                except Exception as e:
                    logger.error(f"Failed to elevate privileges: {e}")
                    self.speak(f"Failed to open {app_name} with administrator privileges.")
            else:
                self.speak("Access denied, even with Administrator privileges.")
        except Exception as e:
            logger.error(f"Failed to open application: {e}")
            self.speak(f"Error opening {app_name}")


    def search_web(self, query: str) -> None:
        """Search the web using default browser."""
        try:
            search_url = f"https://www.google.com/search?q={query}"
            webbrowser.open(search_url)
            self.speak(f"Searching for {query}")
        except Exception as e:
            logger.error(f"Web search error: {e}")
            self.speak("Sorry, I couldn't perform the web search.")

    def get_info(self, query: str) -> None:
        """Get information from Gemini."""
        try:
            chat_session = self.chat_model.start_chat()
            response = chat_session.send_message(query)
            
            if response.text:
                print(f'Assistant: {response.text}\n')
                self.speak(response.text)
            else:
                self.speak("Sorry, I couldn't generate a response.")
        except Exception as e:
            logger.error(f"Error getting information: {e}")
            self.speak("Sorry, I encountered an error while getting that information.")

    
    def _initialize_spotify(self):
        try:
            return spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope="user-modify-playback-state user-read-playback-state"
            ))
        except Exception as e:
            logger.error(f"Spotify initialization error: {e}")
            return None

    def is_spotify_running(self):
        return "Spotify.exe" in (p.name() for p in psutil.process_iter())


    def pause_music(self):
        try:
            devices = self.spotify.devices()
            if not devices['devices']:
                self.speak("No active Spotify devices found")
                return False
                
            self.spotify.pause_playback(device_id=devices['devices'][0]['id'])
            return True
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Spotify API error: {e}")
            return False

  

    def play_music(self, query=None):
        try:
            if not self.spotify:
                self.speak("Spotify is not configured properly")
                return False

            devices = self.spotify.devices()
            if not devices['devices']:
                if not self.is_spotify_running():
                    self.open_application("spotify")
                    time.sleep(3)
                    devices = self.spotify.devices()
                    if not devices['devices']:
                        self.speak("No Spotify devices found")
                        return False

            device_id = devices['devices'][0]['id']

            if query:
                results = self.spotify.search(q=query, type='track', limit=1)
                if not results['tracks']['items']:
                    self.speak("No tracks found for your query")
                    return False
                    
                track = results['tracks']['items'][0]
                self.spotify.start_playback(device_id=device_id, uris=[track['uri']])
            else:
                self.spotify.start_playback(device_id=device_id)
            return True
                    
        except spotipy.exceptions.SpotifyException as e:
            logger.error(f"Spotify API error: {e}")
            self.speak("Error controlling Spotify playback")
            return False
        

    def execute_command(self, command: str) -> bool:
            """Execute voice commands and return False if should exit."""
            if not command:
                return True

            try:
                if any(word in command for word in ["exit", "quit", "stop"]):
                    self.speak("Goodbye!")
                    return False

                if "switch to admin mode" in command:
                    self.is_admin_mode = self.authenticate_admin()
                    return True
                
                if "set up admin passcode" in command:
                    if not self.admin_passphrase:
                        self.setup_admin_passphrase()
                    else:
                        self.speak("Admin passphrase already exists. Please authenticate as admin to change it")
                    return True

                if "hello jarvis" in command:
                    self.speak("Hello! How can I assist you?")
                    return True

                if "what can you do" in command:
                    self.speak("I can perform various tasks, such as searching the web, getting information, opening applications and folders")
                    return True

                if command.startswith("launch"):
                    
                    app_name = command.replace("launch", "").strip()
                    if not app_name:
                        self.speak("Please specify the application to open.")
                        return True
                        
                    if not self.is_admin_mode:
                        self.speak("This command requires admin access. Please switch to admin mode first")
                        return True
                        
                    self.open_application(app_name)
                    return True

                if "open folder" in command:
                    folder_name = command.replace("open folder", "").strip()
                    if not folder_name:
                        self.speak("Please specify the folder to open.")
                        return True
                        
                    if not self.is_admin_mode:
                        self.speak("This command requires admin access. Please switch to admin mode first")
                        return True
                        
                    self.open_folder(folder_name)
                    return True

                if "search" in command:
                    query = command.replace("search for", "").replace("search", "").strip()
                    if query:
                        self.search_web(query)
                    else:
                        self.speak("Please specify what to search for.")
                    return True

                if command.startswith(("get information", "give information")):
                    query = command.replace("get information", "").replace("give information on", "").strip()
                    if query:
                        self.get_info(query)
                    else:
                        self.speak("Please specify what information you need.")
                    return True

                if "music" in command or "play" in command or "pause" in command:
                    if not self.spotify:
                        self.speak("Spotify is not configured")
                        return True
                        
                    if "pause" in command or "stop music" in command:
                        if self.pause_music():
                            self.speak("Music paused")
                        return True
                        
                        
                    if "play" in command:
                        query = command.replace("play", "").strip()
                        if self.play_music(query):
                            self.speak(f"Playing {query if query else 'music'}")
                        return True

                # Rest of your existing command handling code...
                    return True
                                    
                self.speak("I'm not sure how to help with that.")
                return True

            except Exception as e:
                logger.error(f"Error executing command: {e}")
                self.speak("Sorry, I encountered an error.")
                return True

    def run(self) -> None:
        """Main loop of the voice assistant."""
        self.speak("Hello, this is Jarvis your voice assistant. How can I help you?")
        
        while True:
            command = self.listen()
            if not self.execute_command(command):
                break


def main():
    try:
        assistant = VoiceAssistant()
        assistant.run()
    except Exception as e:
        logger.critical(f"Critical error: {e}")
        print("An error occurred. Please check the logs for details.")


# if __name__ == "__main__":
#     main()
###
