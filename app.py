import requests
import time
import json
import os
import sys
from datetime import datetime
from pathlib import Path

class FacebookAutoPoster:
    def __init__(self):
        self.config_file = "config.json"
        self.messages_file = "messages.txt"
        self.load_config()
        
    def load_config(self):
        """Load configuration from file or environment variables"""
        # Default config
        self.config = {
            "cookies": "",
            "group_uid": "",
            "target_name": "",
            "delay": 5
        }
        
        # Try to load from config.json
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                loaded = json.load(f)
                self.config.update(loaded)
                print(f"✅ Loaded config from {self.config_file}")
        
        # Override with environment variables (for Render)
        if os.environ.get('FB_COOKIES'):
            self.config['cookies'] = os.environ.get('FB_COOKIES')
            print("✅ Loaded cookies from environment")
        if os.environ.get('FB_GROUP_UID'):
            self.config['group_uid'] = os.environ.get('FB_GROUP_UID')
            print("✅ Loaded group UID from environment")
        if os.environ.get('FB_DELAY'):
            self.config['delay'] = int(os.environ.get('FB_DELAY'))
            print(f"✅ Loaded delay from environment")
            
        self.messages = []
        
    def save_config(self):
        """Save configuration to file"""
        # Don't save sensitive data if from environment
        if not os.environ.get('FB_COOKIES'):
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
                print(f"✅ Config saved to {self.config_file}")
    
    def load_messages(self):
        """Load messages from file"""
        if not os.path.exists(self.messages_file):
            print(f"❌ {self.messages_file} not found!")
            print("Creating sample messages file...")
            sample_messages = [
                "Hello everyone! Welcome to our group!",
                "Check out our latest updates!",
                "Don't forget to follow group rules.",
                "Share your thoughts and experiences!",
                "Have a great day everyone!"
            ]
            with open(self.messages_file, 'w') as f:
                for msg in sample_messages:
                    f.write(msg + '\n')
            print(f"✅ Created sample {self.messages_file}")
            return sample_messages
        
        with open(self.messages_file, 'r', encoding='utf-8') as f:
            self.messages = [line.strip() for line in f if line.strip()]
        
        print(f"✅ Loaded {len(self.messages)} messages from {self.messages_file}")
        return self.messages
    
    def parse_cookies(self):
        """Parse cookie string to dictionary"""
        cookie_dict = {}
        cookies_str = self.config['cookies']
        
        for cookie in cookies_str.split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                cookie_dict[key] = value
        
        return cookie_dict
    
    def post_to_facebook(self, message, post_number, total_posts):
        """Post message to Facebook group"""
        try:
            if not self.config['cookies']:
                print("❌ No cookies provided! Please set FB_COOKIES environment variable")
                return False
            
            if not self.config['group_uid']:
                print("❌ No group UID provided! Please set FB_GROUP_UID environment variable")
                return False
            
            # Parse cookies
            cookie_dict = self.parse_cookies()
            
            # Method 1: Facebook Graph API (Recommended)
            # You need to create a Facebook App and get access token
            url = f"https://graph.facebook.com/v18.0/{self.config['group_uid']}/feed"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Cookie': self.config['cookies']
            }
            
            payload = {
                'message': message,
                'access_token': cookie_dict.get('access_token', '')
            }
            
            # For demo purposes - simulate successful post
            # In production, uncomment the actual request
            print(f"📤 POSTING ({post_number}/{total_posts}): {message[:50]}...")
            time.sleep(1)  # Simulate network delay
            
            # Uncomment for actual Facebook API call
            """
            response = requests.post(url, data=payload, headers=headers)
            
            if response.status_code == 200:
                post_id = response.json().get('id')
                print(f"✅ Success! Post ID: {post_id}")
                return True
            else:
                print(f"❌ Failed! Status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
            """
            
            # Demo success
            print(f"✅ [DEMO] Post successful!")
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def start_posting(self):
        """Start the auto-posting process"""
        print("\n" + "="*60)
        print("🚀 FACEBOOK AUTO-POSTER STARTED")
        print("="*60)
        
        # Validate config
        if not self.config['cookies']:
            print("\n❌ ERROR: Facebook cookies not set!")
            print("\nHow to set cookies:")
            print("1. Method 1 - Environment Variable (For Render):")
            print("   Set FB_COOKIES environment variable in Render dashboard")
            print("\n2. Method 2 - Config File:")
            print("   Create config.json with:")
            print('   {"cookies": "your_cookies_here"}')
            print("\n3. How to get cookies:")
            print("   - Login to Facebook")
            print("   - Open Developer Tools (F12)")
            print("   - Go to Application/Storage tab")
            print("   - Copy cookies (c_user and xs values)")
            return
        
        if not self.config['group_uid']:
            print("\n❌ ERROR: Group UID not set!")
            print("\nHow to get Group UID:")
            print("   - Open your Facebook group")
            print("   - URL: facebook.com/groups/YOUR_GROUP_ID")
            print("   - Copy the number after /groups/")
            return
        
        # Load messages
        messages = self.load_messages()
        if not messages:
            print("❌ No messages to post!")
            return
        
        total = len(messages)
        print(f"\n📊 Configuration:")
        print(f"   Target: {self.config['target_name'] or self.config['group_uid']}")
        print(f"   Total Messages: {total}")
        print(f"   Delay: {self.config['delay']} seconds")
        print(f"   Cookies: {'✓ Set' if self.config['cookies'] else '✗ Missing'}")
        print("\n" + "="*60)
        
        success_count = 0
        fail_count = 0
        
        for idx, message in enumerate(messages, 1):
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Processing message {idx}/{total}")
            
            success = self.post_to_facebook(message, idx, total)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
            
            # Wait before next post (except for last message)
            if idx < total:
                print(f"⏱️ Waiting {self.config['delay']} seconds before next post...")
                time.sleep(self.config['delay'])
        
        # Final summary
        print("\n" + "="*60)
        print("📊 POSTING COMPLETED!")
        print(f"   ✅ Success: {success_count}")
        print(f"   ❌ Failed: {fail_count}")
        print(f"   📝 Total: {total}")
        print("="*60 + "\n")
    
    def interactive_mode(self):
        """Interactive CLI mode"""
        print("\n" + "="*60)
        print("🤖 FACEBOOK AUTO-POSTER - INTERACTIVE MODE")
        print("="*60)
        
        # Input cookies
        if not self.config['cookies']:
            print("\n📱 Enter your Facebook cookies:")
            print("   (Example: c_user=123456; xs=789012;)")
            cookies_input = input("Cookies: ").strip()
            if cookies_input:
                self.config['cookies'] = cookies_input
        
        # Input group UID
        if not self.config['group_uid']:
            print("\n👥 Enter Group UID:")
            print("   (Example: 123456789012345)")
            group_input = input("Group UID: ").strip()
            if group_input:
                self.config['group_uid'] = group_input
        
        # Input target name
        if not self.config['target_name']:
            target_input = input("\n🎯 Enter Target Name (optional): ").strip()
            if target_input:
                self.config['target_name'] = target_input
        
        # Input delay
        if not self.config['delay']:
            try:
                delay_input = int(input("\n⏱️ Delay between posts (seconds) [default: 5]: ").strip())
                self.config['delay'] = delay_input if delay_input > 0 else 5
            except:
                self.config['delay'] = 5
        
        # Save config
        self.save_config()
        
        # Start posting
        self.start_posting()

def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🌟 FACEBOOK GROUP AUTO-POSTER TOOL v1.0")
    print("="*60)
    
    poster = FacebookAutoPoster()
    
    # Check if running on Render (environment variables)
    if os.environ.get('RENDER'):
        print("\n🖥️ Running on Render platform")
        print("Using environment variables for configuration")
        
        # Auto-start posting if config is set
        if os.environ.get('FB_COOKIES') and os.environ.get('FB_GROUP_UID'):
            print("✅ Configuration found, starting auto-poster...")
            poster.start_posting()
        else:
            print("\n⚠️ Missing configuration!")
            print("Please set these environment variables in Render:")
            print("  - FB_COOKIES: Your Facebook cookies")
            print("  - FB_GROUP_UID: Your group ID")
            print("  - FB_DELAY: Delay in seconds (optional)")
    else:
        # Local mode - interactive
        while True:
            print("\n📌 MAIN MENU")
            print("1. Start Posting")
            print("2. Configure Settings")
            print("3. Load Messages File")
            print("4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                poster.start_posting()
            elif choice == '2':
                poster.interactive_mode()
            elif choice == '3':
                file_path = input("Enter messages file path [messages.txt]: ").strip()
                if file_path:
                    poster.messages_file = file_path
                poster.load_messages()
            elif choice == '4':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid option!")

if __name__ == "__main__":
    main()
