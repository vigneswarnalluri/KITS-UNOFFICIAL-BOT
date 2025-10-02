# Deployment Guide

This guide covers various deployment options for the KITS Bot.

## 🚀 Quick Deploy Options

### 1. Heroku Deployment

#### Method 1: One-Click Deploy
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/your-username/IARE-BOT-V5.2)

#### Method 2: Manual Heroku Deployment

1. **Install Heroku CLI**
   ```bash
   # Windows
   winget install Heroku.HerokuCLI
   
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Linux
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Login to Heroku**
   ```bash
   heroku login
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-bot-name
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set API_ID=your_api_id
   heroku config:set API_HASH=your_api_hash
   heroku config:set BOT_TOKEN=your_bot_token
   heroku config:set DEVELOPER_CHAT_ID=your_developer_chat_id
   heroku config:set MAINTAINER_CHAT_ID=your_maintainer_chat_id
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Scale the Bot**
   ```bash
   heroku ps:scale web=1
   ```

### 2. Railway Deployment

1. **Connect GitHub Repository**
   - Go to [Railway](https://railway.app)
   - Sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Configure Environment Variables**
   - Go to your project dashboard
   - Click on "Variables" tab
   - Add all required environment variables

3. **Deploy**
   - Railway will automatically deploy your bot
   - Check the logs for any errors

### 3. Render Deployment

1. **Create Render Account**
   - Go to [Render](https://render.com)
   - Sign up with GitHub

2. **Create Web Service**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Choose the branch (usually `main`)

3. **Configure Service**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Environment**: Python 3

4. **Set Environment Variables**
   - Add all required environment variables in the dashboard

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

## 🐳 Docker Deployment

### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Expose port (if needed)
EXPOSE 8000

# Run the bot
CMD ["python", "main.py"]
```

### 2. Build and Run

```bash
# Build the image
docker build -t kits-bot .

# Run the container
docker run -d --name kits-bot \
  -e API_ID=your_api_id \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  -e DEVELOPER_CHAT_ID=your_developer_chat_id \
  -e MAINTAINER_CHAT_ID=your_maintainer_chat_id \
  kits-bot
```

### 3. Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  kits-bot:
    build: .
    environment:
      - API_ID=${API_ID}
      - API_HASH=${API_HASH}
      - BOT_TOKEN=${BOT_TOKEN}
      - DEVELOPER_CHAT_ID=${DEVELOPER_CHAT_ID}
      - MAINTAINER_CHAT_ID=${MAINTAINER_CHAT_ID}
      - POSTGRES_USER_ID=${POSTGRES_USER_ID}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DATABASE=${POSTGRES_DATABASE}
      - POSTGRES_HOST=postgres
      - POSTGRES_PORT=5432
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=${POSTGRES_USER_ID}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DATABASE}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

Run with:
```bash
docker-compose up -d
```

## 🔧 Environment Configuration

### Required Variables

```env
# Telegram Configuration
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here

# Admin Configuration
DEVELOPER_CHAT_ID=your_developer_chat_id
MAINTAINER_CHAT_ID=your_maintainer_chat_id
```

### Optional Variables

```env
# PostgreSQL Configuration (for production)
POSTGRES_USER_ID=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DATABASE=kits_bot_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## 📊 Monitoring and Logs

### Heroku
```bash
# View logs
heroku logs --tail

# Check app status
heroku ps
```

### Railway
- Check logs in the Railway dashboard
- Use the built-in monitoring tools

### Docker
```bash
# View logs
docker logs kits-bot

# Follow logs
docker logs -f kits-bot
```

## 🔄 Updates and Maintenance

### Heroku
```bash
# Update the bot
git push heroku main

# Restart the bot
heroku restart
```

### Railway
- Push changes to your GitHub repository
- Railway will automatically redeploy

### Docker
```bash
# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## 🛠️ Troubleshooting

### Common Issues

1. **Bot not starting**
   - Check environment variables
   - Verify API credentials
   - Check logs for errors

2. **Database connection issues**
   - Ensure PostgreSQL is running (if using)
   - Check database credentials
   - Verify network connectivity

3. **Session file issues**
   - Delete session files and restart
   - Check file permissions

4. **Memory issues**
   - Increase memory allocation
   - Optimize database queries
   - Check for memory leaks

### Log Analysis

```bash
# Check for errors
grep -i error bot_errors.log

# Check for warnings
grep -i warning bot_errors.log

# Monitor real-time logs
tail -f bot_errors.log
```

## 🔒 Security Considerations

1. **Environment Variables**
   - Never commit `.env` files
   - Use secure, unique passwords
   - Rotate credentials regularly

2. **Database Security**
   - Use strong database passwords
   - Enable SSL connections
   - Regular backups

3. **Bot Security**
   - Limit admin access
   - Monitor user activities
   - Regular security updates

## 📈 Scaling

### Horizontal Scaling
- Use multiple bot instances
- Load balancer configuration
- Database connection pooling

### Vertical Scaling
- Increase memory allocation
- Optimize database queries
- Use caching mechanisms

## 🔄 Backup and Recovery

### Database Backup
```bash
# PostgreSQL backup
pg_dump -h localhost -U postgres kits_bot_db > backup.sql

# Restore
psql -h localhost -U postgres kits_bot_db < backup.sql
```

### Session Backup
```bash
# Backup session files
tar -czf sessions_backup.tar.gz *.session

# Restore
tar -xzf sessions_backup.tar.gz
```

## 📞 Support

For deployment issues:
1. Check the logs first
2. Verify environment variables
3. Test locally before deploying
4. Create an issue on GitHub with logs
