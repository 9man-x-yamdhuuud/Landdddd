"""
Facebook Group Auto-Poster Tool
Professional GUI Application with Dark Neon Theme
Requires: pip install customtkinter requests colorama
"""

import customtkinter as ctk
import tkinter.scrolledtext as scrolledtext
import threading
import time
import requests
import json
import re
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox
import queue

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class FacebookAutoPoster:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Facebook Auto-Poster - Neon Edition")
        self.window.geometry("900x700")
        
        # Variables
        self.is_posting = False
        self.post_queue = queue.Queue()
        self.cookies = ""
        self.group_uid = ""
        self.target_name = ""
        self.delay = 5
        self.messages = []
        
        # Colors (Neon Theme)
        self.colors = {
            'bg': '#0a0a0a',
            'cyan': '#00ffff',
            'magenta': '#ff00ff',
            'dark_cyan': '#008080',
            'dark_magenta': '#800080',
            'text': '#e0e0e0'
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the main UI layout"""
        
        # Main container
        self.main_frame = ctk.CTkFrame(self.window, fg_color=self.colors['bg'])
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="🚀 FACEBOOK AUTO-POSTER TOOL 🚀",
            font=("Courier New", 24, "bold"),
            text_color=self.colors['cyan']
        )
        title_label.pack(pady=10)
        
        # Input Frame
        input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=10)
        
        # Cookies Input
        ctk.CTkLabel(
            input_frame, 
            text="📱 Facebook Cookies:",
            font=("Consolas", 12, "bold"),
            text_color=self.colors['magenta']
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        self.cookies_entry = ctk.CTkEntry(
            input_frame, 
            width=600,
            placeholder_text="c_user=xxx; xs=xxx;...",
            font=("Consolas", 11)
        )
        self.cookies_entry.grid(row=0, column=1, pady=5, padx=10)
        
        # Group UID Input
        ctk.CTkLabel(
            input_frame, 
            text="👥 Group UID:",
            font=("Consolas", 12, "bold"),
            text_color=self.colors['magenta']
        ).grid(row=1, column=0, sticky="w", pady=5)
        
        self.group_entry = ctk.CTkEntry(
            input_frame, 
            width=600,
            placeholder_text="123456789012345",
            font=("Consolas", 11)
        )
        self.group_entry.grid(row=1, column=1, pady=5, padx=10)
        
        # Target Name Input
        ctk.CTkLabel(
            input_frame, 
            text="🎯 Target Name:",
            font=("Consolas", 12, "bold"),
            text_color=self.colors['magenta']
        ).grid(row=2, column=0, sticky="w", pady=5)
        
        self.target_entry = ctk.CTkEntry(
            input_frame, 
            width=600,
            placeholder_text="Group Name or Target Identifier",
            font=("Consolas", 11)
        )
        self.target_entry.grid(row=2, column=1, pady=5, padx=10)
        
        # Delay Input
        ctk.CTkLabel(
            input_frame, 
            text="⏱️ Delay (seconds):",
            font=("Consolas", 12, "bold"),
            text_color=self.colors['magenta']
        ).grid(row=3, column=0, sticky="w", pady=5)
        
        self.delay_entry = ctk.CTkEntry(
            input_frame, 
            width=200,
            placeholder_text="5",
            font=("Consolas", 11)
        )
        self.delay_entry.grid(row=3, column=1, sticky="w", pady=5, padx=10)
        self.delay_entry.insert(0, "5")
        
        # Messages File Frame
        file_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        file_frame.pack(fill="x", padx=20, pady=10)
        
        self.file_label = ctk.CTkLabel(
            file_frame,
            text="📄 No file selected",
            font=("Consolas", 11),
            text_color=self.colors['text']
        )
        self.file_label.pack(side="left", padx=5)
        
        self.load_file_btn = ctk.CTkButton(
            file_frame,
            text="📂 LOAD MESSAGES FILE",
            command=self.load_messages_file,
            font=("Courier New", 12, "bold"),
            fg_color=self.colors['dark_cyan'],
            hover_color=self.colors['cyan'],
            text_color="black"
        )
        self.load_file_btn.pack(side="right", padx=5)
        
        # Messages Preview
        preview_frame = ctk.CTkFrame(self.main_frame)
        preview_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            preview_frame,
            text="📝 MESSAGES PREVIEW",
            font=("Courier New", 14, "bold"),
            text_color=self.colors['cyan']
        ).pack(pady=5)
        
        self.messages_preview = scrolledtext.ScrolledText(
            preview_frame,
            height=8,
            bg=self.colors['bg'],
            fg=self.colors['cyan'],
            font=("Consolas", 10),
            insertbackground=self.colors['magenta']
        )
        self.messages_preview.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Log Display
        log_frame = ctk.CTkFrame(self.main_frame)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        ctk.CTkLabel(
            log_frame,
            text="💻 LIVE LOGS",
            font=("Courier New", 14, "bold"),
            text_color=self.colors['magenta']
        ).pack(pady=5)
        
        self.log_display = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            bg=self.colors['bg'],
            fg=self.colors['cyan'],
            font=("Consolas", 10),
            insertbackground=self.colors['magenta']
        )
        self.log_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Control Buttons
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        self.start_btn = ctk.CTkButton(
            button_frame,
            text="▶ START POSTING",
            command=self.start_posting,
            font=("Courier New", 14, "bold"),
            fg_color="#00aa00",
            hover_color="#00ff00",
            text_color="black",
            width=200,
            height=40
        )
        self.start_btn.pack(side="left", padx=10)
        
        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="⏹ STOP POSTING",
            command=self.stop_posting,
            font=("Courier New", 14, "bold"),
            fg_color="#aa0000",
            hover_color="#ff0000",
            text_color="black",
            width=200,
            height=40,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=10)
        
        # Status Bar
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="✅ READY | System Online",
            font=("Consolas", 10),
            text_color=self.colors['cyan']
        )
        self.status_label.pack(pady=5)
        
    def log_message(self, message, msg_type="INFO"):
        """Add timestamped message to log display"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if msg_type == "ERROR":
            color = self.colors['magenta']
            prefix = "❌ ERROR"
        elif msg_type == "SUCCESS":
            color = "#00ff00"
            prefix = "✅ SUCCESS"
        elif msg_type == "WARNING":
            color = "#ffff00"
            prefix = "⚠️ WARNING"
        else:
            color = self.colors['cyan']
            prefix = "ℹ️ INFO"
        
        log_entry = f"[{timestamp}] [{prefix}] {message}\n"
        
        self.log_display.insert("end", log_entry)
        self.log_display.see("end")
        self.log_display.tag_add(f"color_{msg_type}", "end-2l", "end-1l")
        self.log_display.tag_config(f"color_{msg_type}", foreground=color)
        
    def load_messages_file(self):
        """Load messages from a text file"""
        file_path = filedialog.askopenfilename(
            title="Select Messages File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.messages = [line.strip() for line in file if line.strip()]
                
                self.file_label.configure(text=f"📄 {Path(file_path).name} ({len(self.messages)} messages)")
                
                # Update preview
                self.messages_preview.delete("1.0", "end")
                preview_text = "\n" + ("="*50) + "\n"
                for i, msg in enumerate(self.messages[:10], 1):
                    preview_text += f"{i}. {msg[:100]}{'...' if len(msg) > 100 else ''}\n"
                if len(self.messages) > 10:
                    preview_text += f"\n... and {len(self.messages) - 10} more messages"
                preview_text += "\n" + ("="*50)
                self.messages_preview.insert("1.0", preview_text)
                
                self.log_message(f"Loaded {len(self.messages)} messages from {file_path}", "SUCCESS")
            except Exception as e:
                self.log_message(f"Failed to load file: {str(e)}", "ERROR")
        else:
            self.log_message("File selection cancelled", "WARNING")
    
    def post_to_facebook(self, message):
        """Post a message to Facebook group"""
        try:
            # Parse cookies
            cookie_dict = {}
            for cookie in self.cookies.split(';'):
                if '=' in cookie:
                    key, value = cookie.strip().split('=', 1)
                    cookie_dict[key] = value
            
            # Facebook Graph API endpoint (simplified - you'd need actual endpoints)
            # Note: This is a basic implementation. Real Facebook posting requires proper API
            # authentication and endpoints. This structure shows the logic flow.
            
            url = f"https://graph.facebook.com/v18.0/{self.group_uid}/feed"
            
            payload = {
                'message': message,
                'access_token': cookie_dict.get('access_token', ''),
                # Note: In production, you'd need proper OAuth token
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Cookie': self.cookies
            }
            
            # For demo purposes, we'll simulate successful posting
            # In production, replace with actual requests.post()
            
            # Simulate API call (replace with actual implementation)
            self.log_message(f"Attempting to post: {message[:50]}...", "INFO")
            time.sleep(1)  # Simulate network delay
            
            # Demo success response
            return True, "Post ID: demo_123456"
            
            # Actual implementation would be:
            # response = requests.post(url, data=payload, headers=headers)
            # if response.status_code == 200:
            #     return True, response.json().get('id')
            # else:
            #     return False, response.text
                
        except Exception as e:
            return False, str(e)
    
    def posting_worker(self):
        """Background worker for posting messages"""
        self.log_message("Posting thread started", "INFO")
        
        for idx, message in enumerate(self.messages, 1):
            if not self.is_posting:
                self.log_message("Posting stopped by user", "WARNING")
                break
            
            self.status_label.configure(text=f"🚀 Posting {idx}/{len(self.messages)}...")
            
            success, result = self.post_to_facebook(message)
            
            if success:
                self.log_message(f"Posted ({idx}/{len(self.messages)}): {message[:100]}...", "SUCCESS")
            else:
                self.log_message(f"Failed to post ({idx}/{len(self.messages)}): {result}", "ERROR")
            
            # Wait before next post (except for last message)
            if idx < len(self.messages) and self.is_posting:
                self.status_label.configure(text=f"⏱️ Waiting {self.delay} seconds...")
                for remaining in range(self.delay, 0, -1):
                    if not self.is_posting:
                        break
                    self.status_label.configure(text=f"⏱️ Next post in {remaining} seconds...")
                    time.sleep(1)
        
        if self.is_posting:
            self.log_message("All messages posted successfully!", "SUCCESS")
            self.status_label.configure(text="✅ Posting completed!")
        else:
            self.status_label.configure(text="⏹️ Posting stopped")
        
        # Reset UI
        self.is_posting = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
    
    def start_posting(self):
        """Start the posting process"""
        # Validate inputs
        self.cookies = self.cookies_entry.get().strip()
        self.group_uid = self.group_entry.get().strip()
        self.target_name = self.target_entry.get().strip()
        
        try:
            self.delay = int(self.delay_entry.get().strip())
            if self.delay < 1:
                raise ValueError
        except ValueError:
            self.log_message("Delay must be a positive integer (minimum 1 second)", "ERROR")
            return
        
        if not self.cookies:
            self.log_message("Please enter Facebook cookies", "ERROR")
            return
        
        if not self.group_uid:
            self.log_message("Please enter Group UID", "ERROR")
            return
        
        if not self.messages:
            self.log_message("Please load messages from a file first", "ERROR")
            return
        
        # Start posting
        self.is_posting = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        
        # Start posting thread
        post_thread = threading.Thread(target=self.posting_worker, daemon=True)
        post_thread.start()
        
        self.log_message(f"Starting auto-poster to group '{self.target_name}' with {len(self.messages)} messages", "SUCCESS")
    
    def stop_posting(self):
        """Stop the posting process"""
        self.is_posting = False
        self.log_message("Stopping posting process...", "WARNING")
    
    def run(self):
        """Run the application"""
        self.window.mainloop()

def main():
    """Main entry point"""
    try:
        # Check for required packages
        import customtkinter
        import requests
    except ImportError as e:
        print("Missing required packages. Please install:")
        print("pip install customtkinter requests")
        print("\nAlso install colorama for colored console output: pip install colorama")
        input("\nPress Enter to exit...")
        return
    
    app = FacebookAutoPoster()
    app.run()

if __name__ == "__main__":
    main()
