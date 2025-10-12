# ⚠️ DATA PERSISTENCE WARNING

## CRITICAL: How Data is Stored

This Trading Journal stores ALL user data in **JSON files** that are tracked in git:

### Data Files:
- `trades.json` - All trading data
- `users.json` - User accounts & passwords
- `accounts.json` - Trading accounts
- `mistakes.json` - Mistakes tracking
- `avoided_trades.json` - Avoided trades log
- `pretrade_analysis.json` - Pre-trade plans
- `mindset_checkins.json` - Mindset check-ins
- `quotes.json` - Admin quotes
- `daily_notes.json` - Daily journal entries
- `settings.json` - App settings

## 🚨 IMPORTANT: Data Loss Prevention

### Problem:
Streamlit Cloud has an **ephemeral file system**. When you deploy a new version:
- ❌ Any changes made by users AFTER deployment are LOST
- ❌ New trades, new users, etc. will be RESET to the git version

### Solution:
**Data files are now tracked in git** to provide persistence. However:

⚠️ **MANUAL SYNC REQUIRED** - You must manually commit and push data files to preserve changes!

## 📋 How to Preserve User Data

### Option 1: Manual Git Sync (Current Method)

**Before deploying code updates:**

```bash
# 1. Download current data from Streamlit Cloud
# Go to: https://share.streamlit.io/ → Your App → Manage App
# Unfortunately, Streamlit Cloud doesn't provide direct file access

# 2. If you have access to the data files locally, commit them:
git add *.json
git commit -m "💾 Backup: Save user data before deployment"
git push origin main

# 3. Then deploy your code changes
git add trading_journal.py  # or other code files
git commit -m "✨ Feature: Your update"
git push origin main
```

### Option 2: Use a Database (RECOMMENDED for Production)

For permanent data persistence, migrate to a database:

**PostgreSQL** (Free tier available)
```python
# Streamlit Cloud supports PostgreSQL connection
# Use Neon, Supabase, or Heroku Postgres free tier
```

**Setup:**
1. Create a PostgreSQL database (e.g., on Neon.tech - free)
2. Add connection string to Streamlit Secrets
3. Migrate JSON files to database tables
4. Update read/write functions to use database

### Option 3: External Storage

Use cloud storage for JSON files:
- **AWS S3** (requires AWS account)
- **Google Cloud Storage** (requires GCP account)
- **Cloudinary** (has free tier)

## 🔒 Privacy & Security

### CRITICAL: Keep Repository PRIVATE!

Since user data is now in git:
- ✅ Make your GitHub repository **PRIVATE**
- ✅ User passwords are stored in plain text (not ideal)
- ✅ Trading data is sensitive financial information

**Security Recommendations:**
1. **MAKE REPO PRIVATE** - Go to GitHub → Settings → Danger Zone → Change visibility
2. Consider encrypting sensitive fields
3. Use environment variables for admin password
4. Implement proper password hashing (bcrypt)

## 📊 Current Setup Status

✅ Data files tracked in git (persistence enabled)  
⚠️ Manual sync required for updates  
⚠️ No automatic backups  
❌ No database (JSON files only)  
❌ No encryption  

## 🎯 Recommended Actions

### Immediate:
1. ✅ **Make GitHub repo PRIVATE** (if not already)
2. ✅ Regularly export/backup your data using the app's export function
3. ⚠️ Be careful with deployments - data may be lost

### Short-term:
1. Implement automatic backups to email or external storage
2. Add password hashing (bcrypt)
3. Create a deployment checklist

### Long-term:
1. **Migrate to PostgreSQL database** (best solution)
2. Implement user authentication with proper security
3. Add automatic data sync/backup system

## 📥 Data Export (Backup)

Users can export their data manually:
1. Go to **📊 All Trades** tab
2. Click **📥 Export** button
3. Download CSV file
4. Save in a safe location

**IMPORTANT:** Encourage all users to regularly export their data!

## 🆘 If Data is Lost

If deployment causes data loss:
1. Check git history: `git log --all -- *.json`
2. Restore from previous commit: `git checkout <commit> -- *.json`
3. Force push if needed: `git push -f origin main`
4. Redeploy on Streamlit Cloud

## 📞 Support

For questions about data persistence:
- Check git history for data file changes
- Review commit logs before deploying
- Test deployments on a separate branch first

---

**Remember:** The current setup works but requires careful management. 
For production use with multiple users, a database is strongly recommended!

