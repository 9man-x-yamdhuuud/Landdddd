from flask import Flask, render_template, request, jsonify
import requests
import time
import json
import threading
from datetime import datetime

app = Flask(__name__)

# Global variables
is_posting = False
posting_thread = None
messages_list = []
logs = []

class FacebookPoster:
    def __init__(self):
        self.cookies = ""
        self.group_uid = ""
        self.delay = 5
        self.is_active = False
    
    def post_message(self, message):
        """Post to Facebook"""
        try:
            # Parse cookies
            cookie_dict = {}
            for cookie in self.cookies.split(';'):
                if '=' in cookie:
                    key, value = cookie.strip().split('=', 1)
                    cookie_dict[key] = value
            
            # Facebook API endpoint
            url = f"https://graph.facebook.com/v18.0/{self.group_uid}/feed"
            
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Cookie': self.cookies
            }
            
            payload = {
                'message': message,
                'access_token': cookie_dict.get('access_token', '')
            }
            
            # For demo - remove in production
            time.sleep(1)
            return True, "Demo Post"
            
            # Actual API call (uncomment for production)
            # response = requests.post(url, data=payload, headers=headers)
            # if response.status_code == 200:
            #     return True, response.json().get('id')
            # return False, response.text
            
        except Exception as e:
            return False, str(e)
    
    def start_posting(self, messages, cookies, group_uid, delay):
        self.cookies = cookies
        self.group_uid = group_uid
        self.delay = delay
        self.is_active = True
        
        add_log("🚀 Posting started!", "success")
        add_log(f"📊 Total messages: {len(messages)}", "info")
        
        for idx, msg in enumerate(messages, 1):
            if not self.is_active:
                add_log("⏹️ Posting stopped by user", "warning")
                break
            
            add_log(f"📤 Posting {idx}/{len(messages)}: {msg[:50]}...", "info")
            
            success, result = self.post_message(msg)
            
            if success:
                add_log(f"✅ Posted successfully! (Post ID: {result})", "success")
            else:
                add_log(f"❌ Failed: {result}", "error")
            
            if idx < len(messages) and self.is_active:
                add_log(f"⏱️ Waiting {delay} seconds...", "info")
                time.sleep(delay)
        
        if self.is_active:
            add_log("🎉 All messages posted successfully!", "success")
        
        self.is_active = False
        return True
    
    def stop_posting(self):
        self.is_active = False
        add_log("⚠️ Stopping posting process...", "warning")

poster = FacebookPoster()

def add_log(message, log_type="info"):
    """Add log entry"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    logs.append({
        'timestamp': timestamp,
        'message': message,
        'type': log_type
    })
    # Keep only last 100 logs
    while len(logs) > 100:
        logs.pop(0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start():
    global is_posting, messages_list
    
    data = request.json
    cookies = data.get('cookies', '')
    group_uid = data.get('group_uid', '')
    delay = int(data.get('delay', 5))
    messages_text = data.get('messages', '')
    
    if not cookies:
        return jsonify({'error': 'Cookies required'}), 400
    if not group_uid:
        return jsonify({'error': 'Group UID required'}), 400
    if not messages_text:
        return jsonify({'error': 'Messages required'}), 400
    
    # Parse messages
    messages_list = [msg.strip() for msg in messages_text.split('\n') if msg.strip()]
    
    if not messages_list:
        return jsonify({'error': 'No valid messages found'}), 400
    
    # Start posting in background thread
    thread = threading.Thread(
        target=poster.start_posting,
        args=(messages_list, cookies, group_uid, delay)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'status': 'started', 'total': len(messages_list)})

@app.route('/api/stop', methods=['POST'])
def stop():
    poster.stop_posting()
    return jsonify({'status': 'stopped'})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify(logs)

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({'is_posting': poster.is_active})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
