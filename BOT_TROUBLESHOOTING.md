# 🔧 Bot Troubleshooting Guide

## 🚨 Bot Not Working - Common Issues & Solutions

### 1. 🔍 **Check Railway Deployment Status**

#### Go to Railway Dashboard:
1. **Open [railway.app](https://railway.app)**
2. **Click on your service**
3. **Check "Deployments" tab**
4. **Look for recent deployment status**

#### What to Look For:
- ✅ **"Deployed"** - Service is running
- ❌ **"Failed"** - Deployment failed
- ⚠️ **"Building"** - Still deploying
- 🔄 **"Redeploying"** - Currently updating

### 2. 🔍 **Check Railway Logs**

#### View Logs:
1. **Go to your service in Railway dashboard**
2. **Click "Logs" tab**
3. **Look for error messages**

#### Common Error Messages:
- ❌ **"ModuleNotFoundError"** - Missing dependencies
- ❌ **"ConnectionError"** - Network issues
- ❌ **"AuthenticationError"** - Invalid bot token
- ❌ **"ImportError"** - Code issues

### 3. 🔍 **Verify Bot Configuration**

#### Check Environment Variables:
In Railway dashboard, verify these are set:
```
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
DEVELOPER_CHAT_ID=your_developer_chat_id
MAINTAINER_CHAT_ID=your_maintainer_chat_id
```

#### Test Bot Token:
1. **Go to [@BotFather](https://t.me/BotFather) on Telegram**
2. **Send `/mybots`**
3. **Click on your bot**
4. **Verify it's active**

### 4. 🔍 **Test Bot Commands**

#### Basic Tests:
1. **Open Telegram**
2. **Search for your bot** (using @your_bot_username)
3. **Send `/start`** command
4. **Check if bot responds**

#### Expected Responses:
- ✅ **`/start`** - Should show welcome message
- ✅ **`/help`** - Should show help menu
- ✅ **`/status`** - Should show bot status

### 5. 🔍 **Common Issues & Solutions**

#### Issue 1: Bot Not Responding
**Possible Causes:**
- Bot token invalid
- Bot not started
- Network issues

**Solutions:**
1. **Check bot token** with @BotFather
2. **Verify environment variables** in Railway
3. **Check Railway logs** for errors

#### Issue 2: "Bot was blocked by the user"
**Solution:**
1. **Unblock the bot** in Telegram
2. **Start a new conversation**
3. **Send `/start`** again

#### Issue 3: "Bot is not running"
**Possible Causes:**
- Railway service stopped
- Code errors
- Missing dependencies

**Solutions:**
1. **Check Railway service status**
2. **View Railway logs**
3. **Redeploy if needed**

#### Issue 4: "ModuleNotFoundError"
**Solution:**
1. **Check requirements.txt** has all dependencies
2. **Redeploy service**
3. **Check build logs**

### 6. 🔍 **Railway-Specific Issues**

#### Issue 1: Service Keeps Restarting
**Check:**
- **Memory usage** (should be < 512MB)
- **CPU usage** (should be low)
- **Error logs** for crashes

#### Issue 2: Bot Starts but Stops
**Check:**
- **Keep-alive functionality** working
- **Database connections** stable
- **Network connectivity**

#### Issue 3: Environment Variables Not Set
**Solution:**
1. **Go to Railway dashboard**
2. **Click "Variables" tab**
3. **Add missing variables**
4. **Redeploy service**

### 7. 🔍 **Quick Diagnostic Steps**

#### Step 1: Check Railway Status
- ✅ Service running?
- ✅ Recent deployments successful?
- ✅ No error logs?

#### Step 2: Test Bot Token
- ✅ Valid with @BotFather?
- ✅ Bot active?
- ✅ Not blocked?

#### Step 3: Test Commands
- ✅ `/start` works?
- ✅ Bot responds?
- ✅ No error messages?

#### Step 4: Check Logs
- ✅ No fatal errors?
- ✅ Bot started successfully?
- ✅ Keep-alive working?

### 8. 🚀 **Quick Fixes**

#### Fix 1: Redeploy Service
1. **Go to Railway dashboard**
2. **Click "Deployments"**
3. **Click "Redeploy"**
4. **Wait for completion**

#### Fix 2: Check Environment Variables
1. **Go to "Variables" tab**
2. **Verify all required variables**
3. **Add missing ones**
4. **Redeploy**

#### Fix 3: Check Bot Token
1. **Go to @BotFather**
2. **Send `/mybots`**
3. **Click on your bot**
4. **Regenerate token if needed**

### 9. 📞 **Still Not Working?**

#### Contact Support:
1. **Check Railway documentation**
2. **Post in Railway community**
3. **Check Telegram bot documentation**

#### Debug Information to Provide:
- **Railway service status**
- **Error logs**
- **Bot token validity**
- **Environment variables**

## 🎯 **Most Common Solutions**

1. **Redeploy service** - Fixes most issues
2. **Check environment variables** - Often missing
3. **Verify bot token** - Common mistake
4. **Check Railway logs** - Shows exact errors

## 🎉 **Success Indicators**

When working correctly:
- ✅ **Railway service shows "Deployed"**
- ✅ **No error logs**
- ✅ **Bot responds to `/start`**
- ✅ **Keep-alive pings every 5 minutes**

**Follow these steps to identify and fix the issue!** 🚀
