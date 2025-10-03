# 🚀 IARE Bot V5.2 - 24/7 Free Deployment Guide

This guide will help you deploy your Telegram bot to run 24/7 for free using various cloud platforms.

## 🎯 Best Free 24/7 Hosting Options

### 1. 🟢 **Railway.app** (RECOMMENDED)
- **Free Tier**: $5 credit monthly (usually enough for bots)
- **Background Workers**: ✅ Supported
- **Setup Time**: 3 minutes
- **Limitations**: Limited resources, but works for bots

### 2. 🔵 **Fly.io** (EXCELLENT)
- **Free Tier**: 3 shared-cpu-1x VMs
- **Background Workers**: ✅ Supported
- **Setup Time**: 5 minutes
- **Limitations**: 160GB-hours/month

### 3. 🟡 **Replit** (EASY)
- **Free Tier**: Always-on repls
- **Background Workers**: ✅ Supported
- **Setup Time**: 2 minutes
- **Limitations**: CPU limits, but works for bots

### 4. ❌ **Render.com** (NOT RECOMMENDED)
- **Free Tier**: Web Services only (no Background Workers)
- **Background Workers**: ❌ Requires $7/month paid plan
- **Setup Time**: N/A
- **Limitations**: Not suitable for free bot hosting

### 2. 🟡 **Railway.app** (Alternative)
- **Free Tier**: $5 credit monthly
- **Limitations**: Limited resources
- **Setup Time**: 3 minutes

### 3. 🔵 **Heroku** (Legacy)
- **Free Tier**: Discontinued (now paid)
- **Alternative**: Use paid plans or other platforms

### 4. 🟠 **PythonAnywhere** (Limited)
- **Free Tier**: Limited CPU seconds
- **Limitations**: Not suitable for 24/7 bots
- **Use Case**: Development only

---

## 🚀 Method 1: Render.com (RECOMMENDED)

### Step 1: Prepare Your Code
1. Ensure all files are in your repository
2. The following files are already created:
   - `render.yaml` - Render configuration
   - `keep_alive.py` - Keep alive script
   - `requirements.txt` - Dependencies

### Step 2: Deploy to Render
1. Go to [render.com](https://render.com)
2. Sign up with GitHub
3. Click "New +" → **"Background Worker"** (NOT Web Service!)
4. Connect your GitHub repository
5. Configure settings:
   - **Name**: `iare-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main_render.py`
6. Add environment variables:
   ```
   BOT_TOKEN=your_bot_token_here
   API_ID=your_api_id_here
   API_HASH=your_api_hash_here
   DEVELOPER_CHAT_ID=your_developer_chat_id
   MAINTAINER_CHAT_ID=your_maintainer_chat_id
   ```
7. Click "Create Web Service"

### Step 3: Prevent Sleep (Important!)
Your bot now includes automatic keep-alive functionality that:
- ✅ Pings external services every 5 minutes
- ✅ Keeps Render awake automatically
- ✅ No additional configuration needed

**Optional Environment Variables:**
```
KEEP_ALIVE_INTERVAL=300
UPTIME_URL=https://httpbin.org/get
```

### Step 4: Monitor Your Bot
- Check logs in Render dashboard
- Bot will restart automatically if it crashes
- Free tier includes 750 hours/month (enough for 24/7)

---

## 🚀 Method 2: Railway.app

### Step 1: Deploy to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will auto-detect Python and deploy

### Step 2: Configure Environment
Add these environment variables in Railway dashboard:
```
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
DEVELOPER_CHAT_ID=your_developer_chat_id
MAINTAINER_CHAT_ID=your_maintainer_chat_id
```

### Step 3: Monitor
- Check logs in Railway dashboard
- Bot runs continuously on free tier

---

## 🐳 Method 3: Docker Deployment

### For VPS/Server Deployment:

1. **Install Docker**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install docker.io docker-compose
   
   # Start Docker
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

2. **Deploy with Docker Compose**:
   ```bash
   # Clone your repository
   git clone <your-repo-url>
   cd IARE-BOT-V5.2-main
   
   # Create .env file with your variables
   cp env.example .env
   # Edit .env with your actual values
   
   # Start the bot
   docker-compose up -d
   ```

3. **Monitor**:
   ```bash
   # Check status
   docker-compose ps
   
   # View logs
   docker-compose logs -f
   
   # Restart if needed
   docker-compose restart
   ```

---

## 🔧 Method 4: Local VPS (Advanced)

### Using a Free VPS:
1. **Oracle Cloud Always Free**:
   - 2 ARM-based VMs
   - 1/8 OCPU, 1GB RAM each
   - Perfect for bots

2. **Google Cloud Free Tier**:
   - $300 credit for 90 days
   - f1-micro instances

3. **AWS Free Tier**:
   - t2.micro instances
   - 12 months free

### Setup on VPS:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip git -y

# Clone repository
git clone <your-repo-url>
cd IARE-BOT-V5.2-main

# Install requirements
pip3 install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/iare-bot.service
```

**Service file content**:
```ini
[Unit]
Description=IARE Bot Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/IARE-BOT-V5.2-main
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable iare-bot
sudo systemctl start iare-bot
sudo systemctl status iare-bot
```

---

## 📊 Monitoring & Maintenance

### 1. **Health Checks**
Your bot includes automatic health checks:
- Database connectivity
- Telegram API connectivity
- Automatic restart on failure

### 2. **Logs Monitoring**
```bash
# View logs
tail -f bot_errors.log

# Check system logs
journalctl -u iare-bot -f
```

### 3. **Uptime Monitoring**
Use services like:
- [UptimeRobot](https://uptimerobot.com) - Free monitoring
- [Pingdom](https://pingdom.com) - Advanced monitoring
- [StatusCake](https://statuscake.com) - Free tier available

---

## 🛠️ Troubleshooting

### Common Issues:

1. **Bot goes offline**:
   - Check logs for errors
   - Verify environment variables
   - Restart the service

2. **Database errors**:
   - Check database file permissions
   - Run cleanup script: `python cleanup.py`

3. **Memory issues**:
   - Monitor memory usage
   - Restart bot periodically
   - Use swap file if needed

### Quick Fixes:
```bash
# Restart bot
sudo systemctl restart iare-bot

# Check status
sudo systemctl status iare-bot

# View logs
sudo journalctl -u iare-bot -n 50
```

---

## 💡 Pro Tips

1. **Use Keep Alive Script**: Prevents sleep on free tiers
2. **Monitor Resources**: Keep an eye on CPU/memory usage
3. **Backup Data**: Regularly backup your database files
4. **Update Dependencies**: Keep requirements.txt updated
5. **Use Health Checks**: Implement monitoring for 24/7 reliability

---

## 🎯 Recommended Setup

**For Beginners**: Use **Render.com** with the provided configuration
**For Advanced Users**: Use **Docker** on a free VPS
**For Development**: Use **Railway.app** for quick testing

---

## 📞 Support

If you encounter issues:
1. Check the logs first
2. Verify all environment variables
3. Ensure your bot token is valid
4. Check platform-specific documentation

**Happy Deploying! 🚀**
