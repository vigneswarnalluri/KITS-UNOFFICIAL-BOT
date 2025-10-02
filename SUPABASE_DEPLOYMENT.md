# 🚀 KITS Bot - Supabase Deployment Guide

This guide will help you deploy the KITS Bot with Supabase database for 60-70 members to use on their devices.

## 📋 Prerequisites

1. **Supabase Account**: Sign up at [supabase.com](https://supabase.com)
2. **Telegram Bot Token**: Get from [@BotFather](https://t.me/BotFather)
3. **Telegram API Credentials**: Get from [my.telegram.org](https://my.telegram.org)
4. **Deployment Platform**: Choose one:
   - [Heroku](https://heroku.com) (Free tier available)
   - [Railway](https://railway.app) (Free tier available)
   - [Render](https://render.com) (Free tier available)
   - [DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform)

## 🗄️ Step 1: Set Up Supabase Database

### 1.1 Create Supabase Project
1. Go to [supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Choose your organization
4. Enter project name: `kits-bot-database`
5. Enter database password (save this!)
6. Choose region closest to your users
7. Click "Create new project"

### 1.2 Get Database Credentials
1. In your Supabase dashboard, go to **Settings > Database**
2. Copy the following information:
   - **Host**: `db.xxxxxxxxxxxxx.supabase.co`
   - **Database name**: `postgres`
   - **Port**: `5432`
   - **User**: `postgres`
   - **Password**: (the one you set during project creation)

### 1.3 Set Up Database Tables
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with your credentials (see Step 2)
4. Run the setup script:
   ```bash
   python setup_supabase.py
   ```

## 🔧 Step 2: Configure Environment Variables

Create a `.env` file with the following variables:

```env
# Telegram Bot Configuration
BOT_TOKEN=your_bot_token_from_botfather
API_ID=your_api_id_from_telegram
API_HASH=your_api_hash_from_telegram

# Developer and Maintainer Chat IDs
DEVELOPER_CHAT_ID=your_developer_chat_id
MAINTAINER_CHAT_ID=your_maintainer_chat_id

# Supabase Database Configuration
SUPABASE_USER=postgres
SUPABASE_PASSWORD=your_supabase_password
SUPABASE_DATABASE=postgres
SUPABASE_HOST=db.xxxxxxxxxxxxx.supabase.co
SUPABASE_PORT=5432
```

## 🚀 Step 3: Deploy to Cloud Platform

### Option A: Heroku Deployment

1. **Install Heroku CLI**: Download from [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

2. **Create Heroku App**:
   ```bash
   heroku create your-kits-bot-name
   ```

3. **Set Environment Variables**:
   ```bash
   heroku config:set BOT_TOKEN=your_bot_token
   heroku config:set API_ID=your_api_id
   heroku config:set API_HASH=your_api_hash
   heroku config:set SUPABASE_USER=postgres
   heroku config:set SUPABASE_PASSWORD=your_supabase_password
   heroku config:set SUPABASE_DATABASE=postgres
   heroku config:set SUPABASE_HOST=your_supabase_host
   heroku config:set SUPABASE_PORT=5432
   ```

4. **Deploy**:
   ```bash
   git add .
   git commit -m "Deploy KITS Bot with Supabase"
   git push heroku main
   ```

### Option B: Railway Deployment

1. **Connect GitHub**: Go to [railway.app](https://railway.app) and connect your GitHub repository

2. **Set Environment Variables**: In Railway dashboard, add all environment variables from Step 2

3. **Deploy**: Railway will automatically deploy your bot

### Option C: Render Deployment

1. **Create Web Service**: Go to [render.com](https://render.com) and create a new Web Service

2. **Connect Repository**: Connect your GitHub repository

3. **Configure**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

4. **Set Environment Variables**: Add all environment variables from Step 2

5. **Deploy**: Click "Deploy"

## 👥 Step 4: Invite Your Members

1. **Get Bot Username**: Your bot will be available at `@your_bot_username`

2. **Share Bot Link**: Send this link to your 60-70 members:
   ```
   https://t.me/your_bot_username
   ```

3. **Bot Commands**: Members can use:
   - `/start` - Start using the bot
   - `/login` - Login with their credentials
   - `/help` - Get help

## 🔧 Step 5: Monitor and Manage

### Monitor Bot Status
- **Heroku**: `heroku logs --tail`
- **Railway**: Check logs in dashboard
- **Render**: Check logs in dashboard

### Manage Users
- Use admin commands to manage users
- Check Supabase dashboard for user data
- Monitor bot performance

## 📊 Database Management

### View Data in Supabase
1. Go to your Supabase project dashboard
2. Navigate to **Table Editor**
3. View tables:
   - `user_sessions` - User login sessions
   - `user_credentials` - Saved credentials
   - `user_settings` - User preferences
   - `reports` - User reports
   - `lab_uploads` - Lab upload data
   - `admins` - Admin users

### Backup Database
1. In Supabase dashboard, go to **Settings > Database**
2. Click "Download backup" to get a SQL dump
3. Store backup securely

## 🛠️ Troubleshooting

### Common Issues

1. **Bot Not Responding**:
   - Check environment variables
   - Check Supabase connection
   - Check deployment logs

2. **Database Connection Issues**:
   - Verify Supabase credentials
   - Check network connectivity
   - Ensure database is accessible

3. **Multiple Bot Instances**:
   - Ensure only one deployment is running
   - Check for duplicate environment variables

### Support
- Check bot logs for errors
- Verify Supabase connection
- Test with a small group first

## 🎉 Success!

Your KITS Bot is now deployed with Supabase database and ready for 60-70 members to use!

### Benefits of Supabase Deployment:
- ✅ **Scalable**: Handles 60-70 users easily
- ✅ **Reliable**: Cloud database with 99.9% uptime
- ✅ **Secure**: Encrypted data transmission
- ✅ **Fast**: Global CDN for quick responses
- ✅ **Managed**: No database maintenance needed

### Next Steps:
1. Test with a few members first
2. Monitor performance
3. Scale as needed
4. Add more features as required

---

**Need Help?** Check the logs, verify your configuration, and ensure all environment variables are set correctly.
