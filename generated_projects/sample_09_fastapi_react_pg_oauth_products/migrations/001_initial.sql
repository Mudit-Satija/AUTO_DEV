CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    oauth_provider VARCHAR(50),
    oauth_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    access_token VARCHAR(512) NOT NULL,
    refresh_token VARCHAR(512),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_tokens_user_id ON tokens(user_id);
CREATE INDEX idx_tokens_access_token ON tokens(access_token);
CREATE INDEX idx_tokens_refresh_token ON tokens(refresh_token);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_oauth_provider ON users(oauth_provider);
CREATE INDEX idx_users_oauth_id ON users(oauth_id);