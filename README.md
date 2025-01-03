# Voice Assistant with GUI

An intelligent voice assistant application built with Python, featuring speech recognition, natural language processing, and a modern graphical user interface. This application combines voice commands with a sleek GUI to provide an intuitive way to control your computer, search the web, manage music playback, and more.

## Features

### Core Capabilities
- Speech recognition and natural language processing
- Text-to-speech feedback
- Modern GUI with dark/light theme support
- Real-time voice activity indication
- Secure admin mode for privileged operations
- Message history with timestamps
- Spotify integration for music playback
- Web search capabilities
- Application and folder management

### User Interface
- Clean, modern design using ttkbootstrap
- Dark/light theme toggle
- Admin mode toggle
- Chat view with message history
- Documentation view with comprehensive guides
- Real-time listening status indicator
- Scrollable message history
- Responsive layout

## Prerequisites

- Python 3.8 or higher
- Internet connection for speech recognition and web services
- Spotify account (for music playback features)
- Windows operating system (for system commands)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/voice-assistant.git
cd voice-assistant
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up Spotify API credentials:
   - Create a Spotify Developer account
   - Create a new application in the Spotify Developer Dashboard
   - Set the redirect URI to "http://localhost:8888/callback/"
   - Copy your Client ID and Client Secret
   - Update the credentials in the code:
     ```python
     CLIENT_ID = "your_client_id"
     CLIENT_SECRET = "your_client_secret"
     ```

5. Set up Google Generative AI:
   - Obtain an API key from Google AI Studio
   - Update the API key in the code:
     ```python
     genai.configure(api_key="your_api_key")
     ```

## Usage

1. Start the application:
```bash
python main.py
```

2. The application will start with both GUI and voice recognition active.

### Voice Commands

- **Wake Word**: "Hello Jarvis"
- **Basic Commands**:
  - "Search for [query]" - Search the web
  - "Get information about [topic]" - Get detailed information
  - "Launch [application]" - Open an application (requires admin mode)
  - "Open folder [name]" - Open a folder (requires admin mode)
  - "Play [song/artist]" - Play music on Spotify
  - "Pause music" - Pause Spotify playback
  - "Exit" or "Quit" - Close the application

### Admin Mode

1. Set up admin passphrase:
   - Say "Set up admin passcode"
   - Follow the voice prompts

2. Enter admin mode:
   - Say "Switch to admin mode"
   - Speak your passphrase when prompted

3. Admin features:
   - Application launching
   - Folder access
   - System commands

### GUI Features

- Toggle between light and dark themes using the sun/moon button
- Switch between chat and documentation views
- View message history with timestamps
- Monitor voice recognition status
- Toggle admin mode
- Access comprehensive documentation

## Project Structure

```
voice-assistant/
├── main.py           # Application entry point
├── speech.py         # Voice assistant core functionality
├── gui.py            # GUI implementation
└── requirements.txt  # Project dependencies
```

## Logging

The application maintains logs in `voice_assistant.log`, recording:
- Command execution
- Error messages
- System status
- Voice recognition events

## Security Features

- Admin mode with voice passphrase authentication
- Secure storage of admin credentials
- Permission-based command execution
- Protected system operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request



## Acknowledgments

- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) for voice recognition
- [pyttsx3](https://pypi.org/project/pyttsx3/) for text-to-speech
- [ttkbootstrap](https://ttkbootstrap.readthedocs.io/) for GUI styling
- [Spotipy](https://spotipy.readthedocs.io/) for Spotify integration
- Google Generative AI for natural language processing