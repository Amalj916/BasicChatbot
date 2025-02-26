import tkinter as tk
from tkinter import scrolledtext, ttk
import logging
import threading
from typing import Dict, List


class ChatbotGUI:
    def __init__(self, root, chatbot_engine):
        self.root = root
        self.chatbot_engine = chatbot_engine
        self.root.title("AI Chatbot")
        self.root.geometry("600x800")

        # Configure grid weight
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.main_frame, wrap=tk.WORD, height=30, font=("Arial", 10)
        )
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.chat_display.config(state="disabled")

        # Create input frame
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Create input field
        self.input_field = ttk.Entry(self.input_frame, font=("Arial", 10))
        self.input_field.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        # Create send button
        self.send_button = ttk.Button(
            self.input_frame, text="Send", command=self.send_message
        )
        self.send_button.grid(row=0, column=1)

        # Bind enter key to send message
        self.input_field.bind("<Return>", lambda e: self.send_message())

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(
            self.main_frame, textvariable=self.status_var, font=("Arial", 9)
        )
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=5)
        self.status_var.set("Ready")

    def append_message(self, message: str, sender: str):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"{sender}: {message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def process_response(self, user_input: str):
        try:
            for event in self.chatbot_engine.stream_graph_updates(user_input):
                self.root.after(0, self.append_message, event, "Assistant")
            self.status_var.set("Ready")
            self.input_field.config(state="normal")
            self.send_button.config(state="normal")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            logging.error(f"Error in process_response: {str(e)}")
            self.input_field.config(state="normal")
            self.send_button.config(state="normal")

    def send_message(self):
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        # Clear input field
        self.input_field.delete(0, tk.END)

        # Display user message
        self.append_message(user_input, "User")

        # Disable input while processing
        self.input_field.config(state="disabled")
        self.send_button.config(state="disabled")
        self.status_var.set("Processing...")

        # Process in separate thread
        threading.Thread(
            target=self.process_response, args=(user_input,), daemon=True
        ).start()

    def set_status(self, message: str):
        self.status_var.set(message)
