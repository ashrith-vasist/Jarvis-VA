# main.py

import threading
from gui import VoiceAssistantGUI
from speech import VoiceAssistant

def main():
    # Create GUI instance
    gui = VoiceAssistantGUI()
    
    # Create voice assistant instance
    assistant = VoiceAssistant()
    assistant.set_gui(gui)
    
    # Run voice assistant in a separate thread
    assistant_thread = threading.Thread(target=assistant.run, daemon=True)
    assistant_thread.start()
    
    # Run GUI (this will block until window is closed)
    gui.run()

if __name__ == "__main__":
    main()