-- ## 5. init.sql (Database initialization)
-- Create database schema
CREATE TABLE IF NOT EXISTS tweets (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(255) UNIQUE,
    date TIMESTAMP,
    username VARCHAR(255),
    content TEXT,
    content_clean TEXT,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    total_engagement INTEGER DEFAULT 0,
    sentiment VARCHAR(50),
    sentiment_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mentions (
    id SERIAL PRIMARY KEY,
    tweet_id VARCHAR(255) UNIQUE,
    date TIMESTAMP,
    username VARCHAR(255),
    content TEXT,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255),
    accuracy FLOAT,
    f1_score FLOAT,
    precision_score FLOAT,
    recall_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tweets_date ON tweets(date);
CREATE INDEX idx_tweets_sentiment ON tweets(sentiment);
CREATE INDEX idx_mentions_date ON mentions(date);