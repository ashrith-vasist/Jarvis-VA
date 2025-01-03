import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
import json
from datetime import datetime
import os

class VoiceAssistantGUI:
    def __init__(self):
        # Initialize main window
        self.root = ttk.Window(themename="litera")
        self.root.title("Voice Assistant")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)

        # State variables
        self.current_view = tk.StringVar(value="chat")
        self.is_admin = tk.BooleanVar(value=False)
        self.is_dark_mode = tk.BooleanVar(value=False)
        self.is_listening = tk.BooleanVar(value=False)

        # Message history
        self.messages = []

        # Create UI
        self.setup_styles()
        self.create_layout()
        self.setup_bindings()

        # Load message history if it exists
        self.load_messages()

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current = self.is_dark_mode.get()
        self.is_dark_mode.set(not current)

        # Update theme
        new_theme = "darkly" if self.is_dark_mode.get() else "litera"
        self.root.style.theme_use(new_theme)

        # Update theme button text
        self.theme_btn.configure(text="☀️" if self.is_dark_mode.get() else "🌙")

    def toggle_admin(self):
        """Toggle admin mode"""
        current = self.is_admin.get()
        self.is_admin.set(not current)

        # Update admin button and label
        self.admin_btn.configure(text="🔓" if self.is_admin.get() else "🔒")
        if self.is_admin.get():
            self.admin_label.pack(side="right")
        else:
            self.admin_label.pack_forget()

    def setup_styles(self):
        style = ttk.Style()
        
        # Enhanced sidebar button style
        style.configure(
            "Sidebar.TButton",
            padding=15,
            width=12,
            font=("Segoe UI", 11)
        )

        # Enhanced message styles for user and assistant
        style.configure(
            "UserMessage.TFrame",
            background="#E3F2FD",
            padding=15,
            borderwidth=1,
            relief="solid"
        )
        
        style.configure(
            "AssistantMessage.TFrame",
            background="#F5F5F5",
            padding=15,
            borderwidth=1,
            relief="solid"
        )

        style.configure(
            "Message.TLabel",
            font=("Segoe UI", 11),
            wraplength=600
        )

    def show_view(self, view_name):
        """Switch between different views in the application"""
        self.current_view.set(view_name)

        # Hide all views first
        self.chat_frame.pack_forget()
        self.docs_frame.pack_forget()

        # Show the requested view
        if view_name == "chat":
            self.chat_frame.pack(fill=tk.BOTH, expand=True)
        elif view_name == "docs":
            self.docs_frame.pack(fill=tk.BOTH, expand=True)

    def setup_bindings(self):
        """Setup keyboard shortcuts and event bindings"""
        # Bind Ctrl+Q to quit
        self.root.bind('<Control-q>', lambda e: self.root.quit())

        # Bind Escape to minimize
        self.root.bind('<Escape>', lambda e: self.root.iconify())

    def load_messages(self):
        """Load message history from file"""
        try:
            if os.path.exists("message_history.json"):
                with open("message_history.json", "r") as f:
                    self.messages = json.load(f)
                    for msg in self.messages:
                        self.display_message(msg["text"], msg["is_user"])
        except Exception as e:
            print(f"Error loading messages: {e}")

    def save_messages(self):
        """Save message history to file"""
        try:
            with open("message_history.json", "w") as f:
                json.dump(self.messages, f)
        except Exception as e:
            print(f"Error saving messages: {e}")

    def add_message(self, text, is_user=True):
        """Add a new message to history"""
        self.messages.append({"text": text, "is_user": is_user, "timestamp": datetime.now().isoformat()})
        self.display_message(text, is_user)
        self.save_messages()

    def display_message(self, text, is_user):
            msg_frame = ttk.Frame(
                self.messages_frame,
                style="UserMessage.TFrame" if is_user else "AssistantMessage.TFrame"
            )
            msg_frame.pack(
                fill="x",
                pady=10,
                padx=20,
                anchor="e" if is_user else "w"
            )

            # Add timestamp
            time_label = ttk.Label(
                msg_frame,
                text=datetime.now().strftime("%H:%M"),
                font=("Segoe UI", 8),
                foreground="gray"
            )
            time_label.pack(anchor="e" if is_user else "w", padx=5)

            # Add message text with enhanced styling
            msg_label = ttk.Label(
                msg_frame,
                text=text,
                style="Message.TLabel",
                justify="right" if is_user else "left"
            )
            msg_label.pack(padx=10, pady=5)

    def create_layout(self):
        """Create the main application layout"""
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create sidebar
        self.create_sidebar()

        # Create main content area
        self.content_container = ttk.Frame(self.main_container)
        self.content_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create views
        self.create_chat_view()
        self.create_docs_view()

        # Show initial view
        self.show_view("chat")

    def create_sidebar(self):
        """Create the sidebar with navigation buttons"""
        sidebar = ttk.Frame(self.main_container, padding="10 20")
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Theme toggle
        self.theme_btn = ttk.Button(
            sidebar,
            text="🌙" if not self.is_dark_mode.get() else "☀️",
            command=self.toggle_theme,
            style="Sidebar.TButton"
        )
        self.theme_btn.pack(pady=(0, 20))

        # Navigation buttons
        ttk.Button(
            sidebar,
            text="💭 Chat",
            command=lambda: self.show_view("chat"),
            style="Sidebar.TButton"
        ).pack(pady=5)

        ttk.Button(
            sidebar,
            text="📚 Docs",
            command=lambda: self.show_view("docs"),
            style="Sidebar.TButton"
        ).pack(pady=5)

        # Admin toggle
        self.admin_btn = ttk.Button(
            sidebar,
            text="🔒" if not self.is_admin.get() else "🔓",
            command=self.toggle_admin,
            style="Sidebar.TButton"
        )
        self.admin_btn.pack(side=tk.BOTTOM, pady=20)

    def set_listening_state(self, state):
        """Set the listening state and update the UI."""
        self.is_listening.set(state)
        if state:
            self.listening_dot.configure(foreground="green")
            self.listening_dot.pack(side=tk.LEFT, padx=5)
        else:
            self.listening_dot.configure(foreground="gray")


    def create_chat_view(self):
        """Create the chat interface"""
        self.chat_frame = ttk.Frame(self.content_container)

        # Chat header
        header = ttk.Frame(self.chat_frame, padding="20")
        header.pack(fill=tk.X)

        ttk.Label(
            header,
            text="Chat Window",
            font=("Segoe UI", 14, "bold")
        ).pack(side=tk.LEFT)

        self.admin_label = ttk.Label(
            header,
            text="Admin Mode",
            font=("Segoe UI", 10),
            foreground="blue"
        )

        # Messages container with scrollbar
        msg_container = ttk.Frame(self.chat_frame)
        msg_container.pack(fill=tk.BOTH, expand=True)

        self.msg_canvas = tk.Canvas(msg_container)
        scrollbar = ttk.Scrollbar(
            msg_container,
            orient="vertical",
            command=self.msg_canvas.yview
        )

        self.messages_frame = ttk.Frame(self.msg_canvas)
        self.messages_frame.bind(
            "<Configure>",
            lambda e: self.msg_canvas.configure(scrollregion=self.msg_canvas.bbox("all"))
        )

        self.msg_canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        self.msg_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.msg_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Listening indicator
        self.listening_frame = ttk.Frame(self.chat_frame, padding="10")
        self.listening_frame.pack(fill=tk.X)

        self.listening_dot = ttk.Label(
            self.listening_frame,
            text="●",
            font=("Segoe UI", 14),
            foreground="green"
        )
        self.listening_dot.pack(side=tk.LEFT, padx=5)

        ttk.Label(
            self.listening_frame,
            text="Listening...",
            font=("Segoe UI", 10)
        ).pack(side=tk.LEFT)

    def create_docs_view(self):
        """Create the documentation view"""
        self.docs_frame = ttk.Frame(self.content_container)
        
        self.docs_canvas = tk.Canvas(self.docs_frame)
        docs_scrollbar = ttk.Scrollbar(self.docs_frame, orient="vertical", 
            command=self.docs_canvas.yview)

        self.docs_content = ttk.Frame(self.docs_canvas, padding="30")
        
        self.docs_content.bind("<Configure>", 
            lambda e: self.docs_canvas.configure(scrollregion=self.docs_canvas.bbox("all")))
        
        self.docs_canvas.bind_all("<MouseWheel>", 
            lambda e: self.docs_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        self.docs_canvas.create_window((0, 0), window=self.docs_content, anchor="nw")
        self.docs_canvas.configure(yscrollcommand=docs_scrollbar.set)

        docs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.docs_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        ttk.Label(self.docs_content, text="Voice Assistant Documentation",
                  
        font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(0, 30))
        sections = [
            ("Overview", [
                "Welcome to your AI-powered Voice Assistant! This intelligent system combines speech recognition, natural language processing, and automation to help you accomplish tasks through voice commands.",
                "The assistant features a modern GUI interface with dark/light mode support, real-time voice activity detection, and secure admin capabilities for advanced functionality.",
                "Key Features:\n- Voice Recognition with Real-time Feedback\n- Natural Language Understanding\n- Task Automation\n- Web Search Integration\n- System Controls\n- Music Playback\n- Customizable Admin Mode"
            ]),
            ("Voice Commands", [
                "Wake Word: 'Hey Assistant' or 'Hello Assistant'",
                "Command Structure: Wake word + Command + Parameters",
                "Example: 'Hey Assistant, search for recent news about artificial intelligence'",
                "The assistant will provide verbal confirmation and visual feedback for all commands"
            ]),
            ("Basic Commands", [
                "General Queries: Ask any question for information",
                "Time & Date: 'What's the time?' or 'What's today's date?'",
                "Weather: 'What's the weather like?' or 'Weather forecast for [location]'",
                "Calculations: 'Calculate [expression]' or 'Convert [units]'",
                "System Status: 'Check system status' or 'How are you?'"
            ]),
            ("Advanced Features", [
                "Web Integration:\n- Web Search: 'Search for [query]'\n- Open Website: 'Open [website]'\n- News Updates: 'Get latest news about [topic]'",
                "System Control:\n- Volume Control: 'Set volume to [level]'\n- Brightness: 'Adjust brightness'\n- System Info: 'Show system information'",
                "Media Control:\n- Play Music: 'Play [song/artist/genre]'\n- Playback Controls: 'Pause', 'Resume', 'Next', 'Previous'\n- Volume: 'Volume up/down'"
            ]),
            ("Admin Features", [
                "Security:\n- Biometric Authentication\n- Custom Wake Word Configuration\n- Command Access Control",
                "System Management:\n- Process Control\n- Network Management\n- System Updates",
                "Custom Automation:\n- Task Scheduling\n- Custom Command Creation\n- Integration Management"
            ]),
            ("Tips & Best Practices", [
                "Speak clearly and at a moderate pace",
                "Use natural language - the assistant understands conversational commands",
                "Check the listening indicator before speaking",
                "For complex tasks, break them into smaller commands",
                "Use admin mode only when necessary for sensitive operations"
            ])
        ]

        for title, content in sections:
            self.create_enhanced_section(title, content)

    def create_enhanced_section(self, title, content):
        """Create an enhanced documentation section"""
        section_frame = ttk.Frame(self.docs_content, padding="20")
        section_frame.pack(fill="x", pady=15)

        title_frame = ttk.Frame(section_frame)
        title_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(title_frame, text="◆", font=("Segoe UI", 14),
            foreground="#2196F3").pack(side="left", padx=(0, 10))

        ttk.Label(title_frame, text=title,
            font=("Segoe UI", 16, "bold")).pack(side="left")

        for item in content:
            content_label = ttk.Label(section_frame, text=item,
                font=("Segoe UI", 11), wraplength=800, justify="left")
            content_label.pack(anchor="w", padx=30, pady=5)

    def create_command_section(self, title, commands):
        """Create a section of commands in the documentation view"""
        section_frame = ttk.Frame(self.docs_frame, padding="10")
        section_frame.pack(fill="x", pady=10)

        ttk.Label(
            section_frame,
            text=title,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 10))

        for command in commands:
            ttk.Label(
                section_frame,
                text=f"• {command}",
                font=("Segoe UI", 10)
            ).pack(anchor="w", padx=20)

    def run(self):
        """Start the GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = VoiceAssistantGUI()
    app.run()