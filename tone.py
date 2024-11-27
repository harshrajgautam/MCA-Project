import time
import json
from pynput import keyboard
import pyautogui
import pyperclip
import groq
import os
import tkinter as tk
from tkinter import ttk
import threading

# Initialize Groq client
client = groq.Groq(api_key="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")

def convert_to_json(text):
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"you are a json creater. you converts users prompt into json. not matter what user say just convert the prompt into json. You are not supposed to respond with anything other than the corrected message. Respond in JSON format with the key 'correctMessage(String)'. Do not respond in plain text.",
            },
            {
                "role": "user",
                "content": text,
            }
        ],
        model="llama3-70b-8192",
        temperature=0,
        max_tokens=1000,
    )
    res = chat_completion.choices[0].message.content
    print(res)
    return json.loads(res)

def improve_text(text, tone):
    prompt = f"Improve the following sentence: '{text}'"
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": f"Improve the sentence, correct grammar, make it sound {tone}, and try to keep the message concise. You are not supposed to respond with anything other than the corrected message. Respond in JSON format with the key 'correctMessage(String)'. Do not respond in plain text. for multiline use \\n",
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-70b-8192",
        temperature=0,
        max_tokens=1000,
    )
    res = chat_completion.choices[0].message.content
    print(res)
    if (is_json(res)):
        return json.loads(res)
    return convert_to_json(res)

def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

def on_press(key):
    try:
        if key == keyboard.Key.f8:
            change_tone("professional")
        elif key == keyboard.Key.f7:
            change_tone("casual")
        elif key == keyboard.Key.f6:
            change_tone("business")
        elif key == keyboard.Key.f5:
            change_tone("conversational")
        elif key == keyboard.Key.f1:
            return False
    except:
        return True

def change_tone(tone):
    pyautogui.hotkey("ctrl", "c")
    original_text = pyperclip.paste()
    print(original_text, tone)
    
    # Improve the text using Groq
    improved_text = improve_text(original_text, tone)
    print(improved_text)

    pyperclip.copy(improved_text['correctMessage'])
    pyautogui.hotkey("ctrl", "v")

class ToneChangerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tone Changer")
        self.root.geometry("800x600")  # Increased window size
        self.listener = None
        self.is_listening = False
        
        # Main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        main_frame.columnconfigure(2, weight=1)
        
        # Left textarea (Input)
        left_frame = ttk.LabelFrame(main_frame, text="Input Text", padding="5")
        left_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.input_text = tk.Text(left_frame, width=40, height=20)
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Center buttons frame
        center_frame = ttk.Frame(main_frame)
        center_frame.grid(row=0, column=1, padx=10, pady=5)
        
        # Tone buttons
        tones = [
            ("Conversational", "conversational"),
            ("Business", "business"),
            ("Casual", "casual"),
            ("Professional", "professional")
        ]
        
        for idx, (label, tone) in enumerate(tones):
            btn = ttk.Button(center_frame, text=f"{label} →", 
                           command=lambda t=tone: self.change_tone_gui(t))
            btn.pack(pady=5)
        
        # Right textarea (Output) with copy button
        right_frame = ttk.LabelFrame(main_frame, text="Output Text", padding="5")
        right_frame.grid(row=0, column=2, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Output textarea
        self.output_text = tk.Text(right_frame, width=40, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Copy button
        copy_button = ttk.Button(right_frame, text="Copy to Clipboard", command=self.copy_output)
        copy_button.pack(pady=5)
        
        # Keyboard listener section
        listener_frame = ttk.LabelFrame(main_frame, text="Keyboard Listener", padding="5")
        listener_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        # Status and toggle button in horizontal layout
        status_frame = ttk.Frame(listener_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_var = tk.StringVar(value="Status: Not Listening")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 12, 'bold'))
        status_label.pack(side=tk.LEFT, padx=5)
        
        self.toggle_button = ttk.Button(status_frame, text="Start Listening", command=self.toggle_listener)
        self.toggle_button.pack(side=tk.RIGHT, padx=5)
        
        # Shortcuts frame
        shortcuts_frame = ttk.Frame(listener_frame)
        shortcuts_frame.pack(fill=tk.X, pady=5)
        
        # Shortcuts list
        shortcuts = [
            ("F5", "Conversational Tone"),
            ("F6", "Business Tone"),
            ("F7", "Casual Tone"),
            ("F8", "Professional Tone"),
            ("F1", "Stop Listener"),
        ]
        
        for idx, (key, description) in enumerate(shortcuts):
            ttk.Label(shortcuts_frame, text=f"{key}:", font=('Arial', 10, 'bold')).grid(row=idx, column=0, padx=5, pady=2, sticky=tk.W)
            ttk.Label(shortcuts_frame, text=description).grid(row=idx, column=1, padx=5, pady=2, sticky=tk.W)
        
        # Configure root grid
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

    def change_tone_gui(self, tone):
        input_text = self.input_text.get("1.0", tk.END).strip()
        if input_text:
            improved = improve_text(input_text, tone)
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert("1.0", improved['correctMessage'])

    def toggle_listener(self):
        if not self.is_listening:
            self.start_listener()
        else:
            self.stop_listener()

    def start_listener(self):
        self.is_listening = True
        self.status_var.set("Status: Listening")
        self.toggle_button.config(text="Stop Listening")
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def stop_listener(self):
        if self.listener:
            self.listener.stop()
        self.is_listening = False
        self.status_var.set("Status: Not Listening")
        self.toggle_button.config(text="Start Listening")

    def copy_output(self):
        output_text = self.output_text.get("1.0", tk.END).strip()
        if output_text:
            pyperclip.copy(output_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = ToneChangerGUI(root)
    root.mainloop()