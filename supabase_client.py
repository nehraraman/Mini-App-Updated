import supabase
import os
from datetime import datetime, timedelta

class SupabaseClient:
    def __init__(self):
        try:
            self.client = supabase.create_client(
                os.getenv('SUPABASE_URL'),
                os.getenv('SUPABASE_KEY')
            )
            print("Supabase client initialized successfully")
        except Exception as e:
            print(f"Error initializing Supabase client: {e}")
            self.client = None
    
    def get_user(self, telegram_id):
        try:
            if not self.client:
                return None
            result = self.client.table('users')\
                .select('*')\
                .eq('telegram_id', telegram_id)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting user {telegram_id}: {e}")
            return None
    
    def create_user(self, user_data):
        try:
            if not self.client:
                return None
            result = self.client.table('users').insert(user_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def update_user(self, telegram_id, updates):
        try:
            if not self.client:
                return None
            result = self.client.table('users')\
                .update(updates)\
                .eq('telegram_id', telegram_id)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating user {telegram_id}: {e}")
            return None
    
    def update_user_coins(self, telegram_id, coins_change, total_earned_change=0):
        user = self.get_user(telegram_id)
        if user:
            new_coins = user['coins'] + coins_change
            new_total = user['total_earned'] + total_earned_change
            
            return self.update_user(telegram_id, {
                'coins': new_coins,
                'total_earned': new_total,
                'updated_at': datetime.utcnow().isoformat()
            })
        return None
    
    def create_ad_session(self, session_data):
        try:
            if not self.client:
                return None
            result = self.client.table('ad_sessions').insert(session_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating ad session: {e}")
            return None
    
    def get_ad_session(self, session_id):
        try:
            if not self.client:
                return None
            result = self.client.table('ad_sessions')\
                .select('*')\
                .eq('session_id', session_id)\
                .eq('verified', False)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting ad session {session_id}: {e}")
            return None
    
    def verify_ad_session(self, session_id):
        try:
            if not self.client:
                return None
            result = self.client.table('ad_sessions')\
                .update({
                    'verified': True, 
                    'verified_at': datetime.utcnow().isoformat()
                })\
                .eq('session_id', session_id)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error verifying ad session {session_id}: {e}")
            return None
    
    def get_today_ad_stats(self, telegram_id):
        try:
            if not self.client:
                return None
            today = datetime.utcnow().date().isoformat()
            result = self.client.table('ad_stats')\
                .select('*')\
                .eq('user_id', telegram_id)\
                .eq('date', today)\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting today ad stats for {telegram_id}: {e}")
            return None
    
    def update_ad_stats(self, telegram_id, ad_type, coins):
        try:
            if not self.client:
                return None
            today = datetime.utcnow().date().isoformat()
            stats = self.get_today_ad_stats(telegram_id)
            
            if stats:
                # Update existing stats
                updates = {
                    'total_coins': stats['total_coins'] + coins,
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                if ad_type == 'popup':
                    updates['popup_views'] = stats['popup_views'] + 1
                else:  # interstitial
                    updates['interstitial_views'] = stats['interstitial_views'] + 1
                
                result = self.client.table('ad_stats')\
                    .update(updates)\
                    .eq('id', stats['id'])\
                    .execute()
            else:
                # Create new stats record
                new_stats = {
                    'user_id': telegram_id,
                    'date': today,
                    'popup_views': 1 if ad_type == 'popup' else 0,
                    'interstitial_views': 1 if ad_type == 'interstitial' else 0,
                    'total_coins': coins
                }
                result = self.client.table('ad_stats').insert(new_stats).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating ad stats for {telegram_id}: {e}")
            return None
    
    def create_boost(self, boost_data):
        try:
            if not self.client:
                return None
            result = self.client.table('boosts').insert(boost_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating boost: {e}")
            return None
    
    def get_active_boost(self, telegram_id):
        try:
            if not self.client:
                return None
            result = self.client.table('boosts')\
                .select('*')\
                .eq('user_id', telegram_id)\
                .eq('is_active', True)\
                .gt('expires_at', datetime.utcnow().isoformat())\
                .execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting active boost for {telegram_id}: {e}")
            return None
    
    def deactivate_boosts(self, telegram_id):
        try:
            if not self.client:
                return None
            result = self.client.table('boosts')\
                .update({'is_active': False})\
                .eq('user_id', telegram_id)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error deactivating boosts for {telegram_id}: {e}")
            return None
    
    def get_active_tasks(self):
        try:
            if not self.client:
                return []
            result = self.client.table('tasks')\
                .select('*')\
                .eq('is_active', True)\
                .execute()
            return result.data
        except Exception as e:
            print(f"Error getting active tasks: {e}")
            return []
    
    def create_task_submission(self, submission_data):
        try:
            if not self.client:
                return None
            result = self.client.table('task_submissions').insert(submission_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating task submission: {e}")
            return None
    
    def create_referral(self, referral_data):
        try:
            if not self.client:
                return None
            result = self.client.table('referrals').insert(referral_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating referral: {e}")
            return None
    
    def get_user_referrals_count(self, telegram_id):
        try:
            if not self.client:
                return 0
            user = self.get_user(telegram_id)
            if user:
                result = self.client.table('referrals')\
                    .select('id', count='exact')\
                    .eq('referrer_id', user['id'])\
                    .execute()
                return len(result.data)
            return 0
        except Exception as e:
            print(f"Error getting referrals count for {telegram_id}: {e}")
            return 0

# Global instance
db = SupabaseClient()