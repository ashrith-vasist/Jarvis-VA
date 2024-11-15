import speech_recognition as sr
import pyttsx3
import requests  # For API calls
import os
import wikipedia
import nltk
from datetime import datetime

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Initialize the speech recognizer and TTS engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Configure voice properties
voices = tts_engine.getProperty('voices')
tts_engine.setProperty('voice', voices[1].id)  # Use female voice (can be adjusted)
tts_engine.setProperty('rate', 150)

# Deep Search API configuration
API_KEY = "YOUR_DEEPSEARCH_API_KEY"  # Replace with your actual API key
SEARCH_ENDPOINT = "https://api.deepsearch.com/search"

# Functions for different tasks
def speak(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"User said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("I didn't catch that. Could you please repeat?")
            return ""
        except sr.RequestError:
            speak("Service is down at the moment. Please try again later.")
            return ""

def open_application(app_name):
    paths = {
        "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
        "notepad": "C:/Windows/system32/notepad.exe",
        "calculator": "C:/Windows/system32/calc.exe"
    }
    path = paths.get(app_name)
    if path:
        os.startfile(path)
        speak(f"Opening {app_name}")
    else:
        speak("Application not found in my list.")

def search_deep(query):
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        payload = {"query": query}
        response = requests.post(SEARCH_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for 4XX/5XX errors
        results = response.json().get("results", [])
        if results:
            top_result = results[0].get("title", "No title") + ": " + results[0].get("snippet", "No details available")
            speak(f"Here's the top result: {top_result}")
        else:
            speak("No results found.")
    except requests.RequestException as e:
        speak("There was an error with the Deep Search service.")
        print(e)

def fetch_wikipedia_info(topic):
    try:
        summary = wikipedia.summary(topic, sentences=2)
        speak(summary)
    except wikipedia.exceptions.DisambiguationError:
        speak("There are multiple entries. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("I couldn't find any information on that topic.")

def execute_command(command):
    if "open" in command:
        if "chrome" in command:
            open_application("chrome")
        elif "notepad" in command:
            open_application("notepad")
        elif "calculator" in command:
            open_application("calculator")
        else:
            speak("I can't open that application.")

    elif "search for" in command:
        query = command.replace("search for", "").strip()
        search_deep(query)

    elif "tell me about" in command:
        topic = command.replace("tell me about", "").strip()
        fetch_wikipedia_info(topic)

    elif "exit" in command or "stop" in command:
        speak("Goodbye!")
        exit()

def main():
    speak("Hello! I am your voice assistant. How can I help you today?")
    while True:
        command = listen()
        if command:
            execute_command(command)

if __name__ == "__main__":
    main()
