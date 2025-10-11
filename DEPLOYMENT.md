# Deployment Guide 🚀

## Option 1: Streamlit Community Cloud (EASIEST & FREE) ⭐

### Step 1: Push to GitHub

```bash
# In your TradeJournal folder
git add .
git commit -m "Initial commit - Trading Journal Pro"

# Create a new repository on GitHub (https://github.com/new)
# Then run:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **"Sign in with GitHub"**
3. Click **"New app"**
4. Fill in:
   - **Repository**: Select your GitHub repo
   - **Branch**: `main`
   - **Main file path**: `trading_journal.py`
5. Click **"Deploy!"**

**That's it!** Your app will be live at: `https://YOUR_USERNAME-YOUR_REPO_NAME.streamlit.app`

### ⚠️ Important Notes for Streamlit Cloud:
- Free tier includes: **Unlimited apps, 1GB storage per app**
- Data persists as long as app is running
- **Restarting the app will reset data** unless you use database
- For production, consider using a database (see below)

---

## Option 2: Heroku (More Control)

### Prerequisites
```bash
# Install Heroku CLI
# Windows: https://devcenter.heroku.com/articles/heroku-cli
# Mac: brew tap heroku/brew && brew install heroku
```

### Deploy
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-trading-journal

# Deploy
git push heroku main

# Open app
heroku open
```

**Cost**: $7/month for Eco dynos

---

## Option 3: Your Own Server (Most Control)

### Using DigitalOcean Droplet

1. **Create Droplet** (Ubuntu 22.04)
   - $6/month for basic droplet
   - Get $200 credit: https://try.digitalocean.com/freetrialoffer/

2. **SSH into server**
```bash
ssh root@YOUR_SERVER_IP
```

3. **Install dependencies**
```bash
# Update system
apt update && apt upgrade -y

# Install Python
apt install python3-pip python3-venv -y

# Clone your repo
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

4. **Run with systemd (runs forever)**
```bash
# Create service file
nano /etc/systemd/system/trading-journal.service
```

Add this:
```ini
[Unit]
Description=Trading Journal Streamlit App
After=network.target

[Service]
User=root
WorkingDirectory=/root/YOUR_REPO_NAME
Environment="PATH=/root/YOUR_REPO_NAME/venv/bin"
ExecStart=/root/YOUR_REPO_NAME/venv/bin/streamlit run trading_journal.py --server.port=8501 --server.address=0.0.0.0

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
systemctl daemon-reload
systemctl enable trading-journal
systemctl start trading-journal

# Check status
systemctl status trading-journal
```

5. **Setup Nginx (for HTTPS)**
```bash
# Install Nginx
apt install nginx -y

# Configure
nano /etc/nginx/sites-available/trading-journal
```

Add:
```nginx
server {
    listen 80;
    server_name YOUR_DOMAIN.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/trading-journal /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Install SSL (free)
apt install certbot python3-certbot-nginx -y
certbot --nginx -d YOUR_DOMAIN.com
```

---

## 🔒 Adding Password Protection

For Streamlit Cloud, add authentication:

### Method 1: Streamlit-Authenticator (Recommended)

1. Install package:
```bash
pip install streamlit-authenticator
```

2. Add to top of `trading_journal.py`:
```python
import streamlit_authenticator as stauth

# Configuration
names = ['Your Name', 'Team Member']
usernames = ['user1', 'user2']
passwords = ['password1', 'password2']  # Use hashed passwords in production

# Create authenticator
hashed_passwords = stauth.Hasher(passwords).generate()
authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords,
    'trading_journal', 'abcdef', cookie_expiry_days=30
)

# Login
name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    authenticator.logout('Logout', 'main')
    st.write(f'Welcome *{name}*')
    # Your app code here
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
    st.stop()
```

### Method 2: Environment Variables (Simpler)

Add to top of `trading_journal.py`:
```python
import os

# Simple password check
def check_password():
    def password_entered():
        if st.session_state["password"] == os.getenv("APP_PASSWORD", "your_password"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Password incorrect")
        return False
    else:
        return True

if not check_password():
    st.stop()

# Your app code continues here...
```

---

## 💾 Using a Database (For Production)

For persistent data across restarts:

### Option: Supabase (Free PostgreSQL)

1. Sign up at https://supabase.com (free tier)
2. Create a new project
3. Install package:
```bash
pip install supabase
```

4. Replace JSON storage with database (I can help with this if needed)

---

## 📊 Monitoring

### Streamlit Cloud
- Built-in logs and monitoring
- View at: `https://share.streamlit.io/`

### Your Server
```bash
# View logs
journalctl -u trading-journal -f

# Check resource usage
htop
```

---

## 🆘 Troubleshooting

### App won't start on Streamlit Cloud
- Check `requirements.txt` has all dependencies
- View logs in Streamlit Cloud dashboard
- Make sure Python version is compatible

### Data disappears after restart
- Expected behavior for file-based storage
- Use database for persistence
- Or download backups regularly using Export feature

### Slow performance
- Streamlit Cloud free tier has resource limits
- Consider upgrading or using your own server
- Optimize data loading (cache functions)

---

## 🎯 Recommended Setup

**For personal use**: Streamlit Community Cloud (free, easy)
**For team (2-5 people)**: Streamlit Cloud with authentication
**For team (5+ people)**: DigitalOcean + Database + Authentication
**For enterprise**: AWS/Azure with proper security

---

Need help? Open an issue on GitHub!

