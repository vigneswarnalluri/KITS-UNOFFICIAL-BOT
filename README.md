# KITS UNOFFICIAL BOT

A Telegram Bot that scrapes data from the [KITS Guntur ERP](https://kitsgunturerp.com/BeesERP/Login.aspx) and provides calculated Attendance, Biometric data, and other student information.

## 🚀 Features

- **Student Information**: View attendance, biometric data, GPA, certificates, and payment details
- **Lab Records**: Upload, manage, and compress lab PDF files
- **User Management**: Admin panel with user statistics and management tools
- **Database Support**: SQLite (default) and PostgreSQL (optional)
- **Secure Authentication**: Telegram-based authentication system

## 📋 Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org/auth))
- PostgreSQL (optional, for production deployments)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/IARE-BOT-V5.2.git
cd IARE-BOT-V5.2
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the environment template and configure your variables:

```bash
cp env.example .env
```

Edit `.env` file with your actual values:

```env
# Telegram Bot Configuration
API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here

# Developer and Maintainer Chat IDs
DEVELOPER_CHAT_ID=your_developer_chat_id
MAINTAINER_CHAT_ID=your_maintainer_chat_id

# PostgreSQL Database Configuration (Optional)
POSTGRES_USER_ID=postgres
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DATABASE=kits_bot_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 4. Run the Bot

```bash
python main.py
```

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | How to Get |
|----------|-------------|------------|
| `API_ID` | Telegram API ID | [my.telegram.org](https://my.telegram.org/auth) |
| `API_HASH` | Telegram API Hash | [my.telegram.org](https://my.telegram.org/auth) |
| `BOT_TOKEN` | Bot Token | [@BotFather](https://t.me/BotFather) |
| `DEVELOPER_CHAT_ID` | Developer Chat ID | [@RawDataBot](https://t.me/raw_data_bot) |
| `MAINTAINER_CHAT_ID` | Maintainer Chat ID | [@RawDataBot](https://t.me/raw_data_bot) |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER_ID` | PostgreSQL Username | postgres |
| `POSTGRES_PASSWORD` | PostgreSQL Password | - |
| `POSTGRES_DATABASE` | Database Name | kits_bot_db |
| `POSTGRES_HOST` | Database Host | localhost |
| `POSTGRES_PORT` | Database Port | 5432 |

## 📱 Usage

### User Commands

- `/start` - Start the bot and get a greeting
- `/login {username} {password}` - Log in with your KITS credentials
- `/logout` - Log out from the current session
- `/report {your report}` - Send a report to the bot developer
- `/help` - Get help information
- `/settings` - View and modify your settings

### User Buttons

- **Attendance** - View your attendance details
- **Biometric** - View your biometric details
- **Bunk** - View the number of classes you can bunk
- **Labs Records** - Upload, view, and delete lab records
- **Student Info** - Get your GPA, certificates, payment details, and profile
- **Logout** - Log out from the current session
- **Saved Username** - Display and manage saved username

### Settings Options

- **Attendance Threshold** - Adjust the attendance threshold
- **Biometric Threshold** - Adjust the biometric threshold
- **Title Extract** - Choose between automatic or manual title extraction for lab records
- **User Interface** - Select between traditional and updated UI

### Admin Commands

> **Note**: These commands are only accessible to BOT_DEVELOPER and BOT_MAINTAINER

- `/reply {your reply}` - Send a reply to user requests
- `/rshow` - Show all pending requests
- `/rclear` - Clear all requests
- `/lusers` - Show the list of users
- `/tusers` - Show the total number of users
- `/reset` - Reset the SQLite database
- `/admin` - Access admin panel with buttons
- `/announce` - Send announcements to all users
- `/ban {username}` - Ban a user
- `/unban {username}` - Unban a user
- `/authorize` - Authorize and add admin

### Admin Buttons

- **Requests** - View all pending requests
- **Users** - View user statistics and lists
- **Database (SQLite3)** - Reset the SQLite3 database
- **Database (PostgreSQL)** - View and manage PostgreSQL database
- **Maintainer Panel** - Access maintainer-specific features

## 🚀 Deployment

### Local Deployment

1. Follow the installation steps above
2. Configure your environment variables
3. Run: `python main.py`

### Production Deployment

#### Using Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/your-username/IARE-BOT-V5.2)

1. Click the deploy button above
2. Configure the environment variables in Heroku dashboard
3. The bot will automatically start


#### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

## 📁 Project Structure

```
IARE-BOT-V5.2/
├── main.py                 # Main bot file
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore file
├── DATABASE/              # Database modules
├── METHODS/               # Core functionality modules
├── Buttons/               # Button handlers
├── CONFIGURE/             # Configuration files
└── README.md              # This file
```

## 🔒 Security

- All sensitive data is stored securely
- Session files are automatically managed
- Database credentials are environment-based
- User authentication is handled through Telegram

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**: Check your BOT_TOKEN and API credentials
2. **Database errors**: Ensure PostgreSQL is running (if using) or check SQLite permissions
3. **Session errors**: Delete session files and restart the bot
4. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

### Logs

Check the `bot_errors.log` file for detailed error information.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please respect the terms of service of KITS Guntur ERP.

## ⚠️ Disclaimer

This is an unofficial bot and is not affiliated with KITS Guntur. Use at your own risk. The developers are not responsible for any issues arising from the use of this bot.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact the maintainers through the bot

---

**Note**: Replace `your-username` in the GitHub URLs with your actual GitHub username.