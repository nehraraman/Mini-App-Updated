from http.server import BaseHTTPRequestHandler
import json
import secrets
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from supabase_client import db
from utils import check_boost_eligibility

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
            
            if self.path == '/api/ads/create_session':
                telegram_id = data.get('telegram_id')
                ad_type = data.get('ad_type')
                
                user = db.get_user(telegram_id)
                if not user:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': False, 'error': 'User not found'}).encode())
                    return
                
                session_id = secrets.token_urlsafe(32)
                ad_session_data = {
                    'user_id': user['id'],
                    'ad_type': ad_type,
                    'session_id': session_id,
                    'coins_earned': 0,
                    'verified': False
                }
                
                db.create_ad_session(ad_session_data)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'session_id': session_id}).encode())
                
            elif self.path == '/api/ads/verify':
                session_id = data.get('session_id')
                
                ad_session = db.get_ad_session(session_id)
                if not ad_session:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': False, 'error': 'Invalid session'}).encode())
                    return
                
                if ad_session['ad_type'] == 'popup':
                    coins = 250
                else:
                    coins = 400
                
                user = db.get_user(ad_session['user_id'])
                db.update_user_coins(user['telegram_id'], coins, coins)
                db.verify_ad_session(session_id)
                db.update_ad_stats(user['telegram_id'], ad_session['ad_type'], coins)
                
                boost_eligible = check_boost_eligibility(user['telegram_id'])
                updated_user = db.get_user(user['telegram_id'])
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True,
                    'coins_earned': coins,
                    'new_balance': updated_user['coins'],
                    'boost_eligible': boost_eligible
                }).encode())
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())