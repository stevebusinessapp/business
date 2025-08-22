# 🚀 Multi-Purpose Business Application - Portable Setup Instructions

## 📋 What You Need to Do

### Step 1: Copy the Project
1. Copy the entire project folder to the target Windows computer
2. Make sure all files are in the same directory structure

### Step 2: Install Python (Required)
1. Download Python 3.8+ from: https://www.python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Restart the computer after installation

### Step 3: Run Complete Setup (One Time)
1. **Double-click** `Complete_Setup.bat`
2. Wait for the setup to complete (5-10 minutes)
3. This will install all dependencies and create a desktop shortcut

### Step 4: Start Using the Application
1. **Double-click** the desktop shortcut "Multi-Purpose Business App"
2. OR double-click `Start_Application_Silent.vbs`
3. The application will open in your browser automatically
4. Register a new account and start using the application

## 📁 Files Created for You

| File | Purpose | Usage |
|------|---------|-------|
| `Complete_Setup.bat` | **One-time setup** | Run this first to install everything |
| `Start_Application_Silent.vbs` | **Silent launcher** | Double-click to start (no console window) |
| `Start_Application.bat` | **Console launcher** | Double-click to start (shows console) |
| `Create_Desktop_Shortcut.bat` | **Create shortcut** | Creates desktop shortcut |
| `launch_app.py` | **Main launcher** | Python script that starts the server |
| `verify_setup.py` | **Verify setup** | Check if everything is working |
| `PORTABLE_SETUP_README.md` | **Detailed guide** | Complete documentation |

## 🎯 Quick Start Guide

### For New Users:
1. **Install Python** (if not already installed)
2. **Run** `Complete_Setup.bat` (one time only)
3. **Double-click** desktop shortcut to start
4. **Register** and start using the application

### For Experienced Users:
1. **Double-click** `Start_Application_Silent.vbs`
2. Application opens in browser automatically
3. **Register** and start using

## 🔧 Troubleshooting

### If Python is not found:
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH"
- Restart computer after installation

### If PowerShell execution policy error:
- Open PowerShell as Administrator
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Type `Y` to confirm

### If port 8000 is in use:
- Close other applications using port 8000
- Or restart your computer

### If setup fails:
- Run `verify_setup.py` to check what's wrong
- Make sure you have internet connection
- Check if antivirus is blocking the application

## 🌐 Application Features

Once running, you can access:

- **Dashboard**: Overview of your business
- **Invoices**: Create and manage invoices
- **Inventory**: Track products and stock
- **Clients**: Manage customer information
- **Job Orders**: Track work orders
- **Quotations**: Generate quotes
- **Receipts**: Track payments
- **Waybills**: Manage shipping
- **Accounting**: Financial tracking

## 🔒 Security & Data

- **Local Only**: Application runs on your computer only
- **No Internet Required**: After initial setup, works offline
- **Local Database**: All data stored locally in SQLite
- **No External Servers**: Your data stays on your computer

## 📞 Support

If you have issues:

1. **Check** the troubleshooting section above
2. **Run** `verify_setup.py` to diagnose problems
3. **Try** running `Start_Application.bat` to see error messages
4. **Ensure** all files are in the same directory
5. **Check** you have at least 500MB free disk space

## 🎉 Success!

Once everything is working:

- The application will open in your browser
- You can register a new account
- Start managing your business immediately
- All data is saved locally on your computer
- No internet required for daily use

---

**Happy Business Management! 🚀**
