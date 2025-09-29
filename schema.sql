-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id TEXT UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    coins INTEGER DEFAULT 0,
    total_earned INTEGER DEFAULT 0,
    referral_code TEXT UNIQUE,
    referred_by TEXT,
    channel_joined BOOLEAN DEFAULT FALSE,
    group_joined BOOLEAN DEFAULT FALSE,
    last_daily_claim TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    instructions TEXT,
    reward INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    proof_required BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Task submissions table
CREATE TABLE task_submissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
    proof_text TEXT,
    status TEXT DEFAULT 'pending',
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ad sessions table
CREATE TABLE ad_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    ad_type TEXT NOT NULL,
    session_id TEXT UNIQUE NOT NULL,
    coins_earned INTEGER DEFAULT 0,
    verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ad stats table
CREATE TABLE ad_stats (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    date DATE DEFAULT CURRENT_DATE,
    popup_views INTEGER DEFAULT 0,
    interstitial_views INTEGER DEFAULT 0,
    total_coins INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, date)
);

-- Boosts table
CREATE TABLE boosts (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    activated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Referrals table
CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    referrer_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    referred_id TEXT NOT NULL,
    coins_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Daily claims table
CREATE TABLE daily_claims (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    claimed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    coins_earned INTEGER DEFAULT 0
);

-- Insert some sample tasks
INSERT INTO tasks (title, description, instructions, reward, is_active) VALUES
('Join our Telegram Channel', 'Join our official Telegram channel and stay updated', 'Join the channel and keep notifications on', 100, true),
('Follow us on Twitter', 'Follow our Twitter account for latest updates', 'Follow and retweet our latest post', 150, true),
('Share with Friends', 'Share this bot with 5 friends', 'Share your referral code with friends', 200, true),
('Watch Tutorial Video', 'Watch our tutorial video on YouTube', 'Watch the video till end and like it', 120, true);

-- Create indexes for better performance
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_referral_code ON users(referral_code);
CREATE INDEX idx_ad_sessions_session_id ON ad_sessions(session_id);
CREATE INDEX idx_ad_sessions_verified ON ad_sessions(verified);
CREATE INDEX idx_ad_stats_user_date ON ad_stats(user_id, date);
CREATE INDEX idx_boosts_user_active ON boosts(user_id, is_active);
CREATE INDEX idx_boosts_expires ON boosts(expires_at);