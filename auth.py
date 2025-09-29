from http.server import BaseHTTPRequestHandler
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from supabase_client import db
from utils import generate_referral_code

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            telegram_id = str(data.get('telegram_id'))
            username = data.get('username')
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            referred_by = data.get('referred_by')
            
            user = db.get_user(telegram_id)
            
            if not user:
                user_data = {
                    'telegram_id': telegram_id,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'coins': 0,
                    'total_earned': 0,
                    'referral_code': generate_referral_code(),
                    'channel_joined': False,
                    'group_joined': False
                }
                
                user = db.create_user(user_data)
                
                if referred_by:
                    referrer = db.get_user(referred_by)
                    if referrer:
                        referral_bonus = 100
                        db.update_user_coins(referrer['telegram_id'], referral_bonus, referral_bonus)
                        
                        db.create_referral({
                            'referrer_id': referrer['id'],
                            'referred_id': telegram_id,
                            'coins_earned': referral_bonus
                        })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'user_id': user['id'],
                'telegram_id': user['telegram_id'],
                'coins': user['coins'],
                'referral_code': user['referral_code'],
                'channel_joined': user.get('channel_joined', False),
                'group_joined': user.get('group_joined', False),
                'channel_link': os.getenv('CHANNEL_LINK', 'https://t.me/your_channel'),
                'group_link': os.getenv('GROUP_LINK', 'https://t.me/your_group')
            }).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())