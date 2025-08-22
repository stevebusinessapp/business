# Multi-Purpose Business Application - Portable Setup

This guide will help you set up the Multi-Purpose Business Application on any Windows computer, even without Python installed.

## 🚀 Quick Start (Recommended)

### Option 1: One-Click Setup
1. **Double-click** `Create_Desktop_Shortcut.bat`
2. This will create a desktop shortcut
3. **Double-click** the desktop shortcut to start the application
4. The application will automatically open in your browser

### Option 2: Direct Launch
- **Double-click** `Start_Application_Silent.vbs` (runs silently)
- **Double-click** `Start_Application.bat` (shows console window)

## 📋 Prerequisites

### Required: Python Installation
The application requires Python 3.8 or higher. If Python is not installed:

1. Download Python from: https://www.python.org/downloads/
2. **IMPORTANT**: During installation, check "Add Python to PATH"
3. Restart your computer after installation

### Optional: PowerShell Execution Policy
If you encounter PowerShell execution policy errors:
1. Open PowerShell as Administrator
2. Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Type `Y` to confirm

## 🔧 First-Time Setup

When you run the application for the first time, it will:

1. ✅ Check if Python is installed
2. ✅ Create a virtual environment
3. ✅ Install all required packages (may take 5-10 minutes)
4. ✅ Set up the database
5. ✅ Start the web server
6. ✅ Open the application in your browser

**Note**: The first run may take several minutes to complete the setup.

## 🌐 Using the Application

Once the application starts:

1. **Register**: Create a new account on the registration page
2. **Login**: Use your credentials to access the dashboard
3. **Explore**: Navigate through the various business modules:
   - 📊 Dashboard
   - 💰 Invoices
   - 📦 Inventory
   - 👥 Clients
   - 📋 Job Orders
   - 📄 Quotations
   - 🧾 Receipts
   - 📤 Waybills
   - 💼 Accounting

## 🛠️ Troubleshooting

### Common Issues:

#### "Python is not installed"
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation
- Restart your computer

#### "PowerShell execution policy error"
- Open PowerShell as Administrator
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Type `Y` to confirm

#### "Port 8000 is already in use"
- Close other applications that might be using port 8000
- Or restart your computer

#### "Application won't start"
- Try running `Start_Application.bat` to see error messages
- Check if your antivirus is blocking the application
- Make sure you have internet connection for the first setup

### Manual Database Reset
If you need to reset the database:
1. Delete the `db.sqlite3` file
2. Restart the application
3. The database will be recreated automatically

## 📁 File Structure

```
multi_purpose_app/
├── Start_Application_Silent.vbs    # Silent launcher (recommended)
├── Start_Application.bat           # Console launcher
├── Start_Application.ps1           # PowerShell launcher
├── Create_Desktop_Shortcut.bat     # Creates desktop shortcut
├── launch_app.py                   # Main launcher script
├── requirements.txt                # Python dependencies
├── business_app/                   # Django project
├── apps/                          # Application modules
├── static/                        # Static files
├── templates/                     # HTML templates
└── PORTABLE_SETUP_README.md       # This file
```

## 🔒 Security Notes

- The application runs locally on your computer
- Data is stored in a local SQLite database
- No data is sent to external servers
- The application uses a development server for simplicity

## 📞 Support

If you encounter any issues:

1. Check the troubleshooting section above
2. Try running `Start_Application.bat` to see detailed error messages
3. Make sure all files are in the same directory
4. Ensure you have sufficient disk space (at least 500MB free)

## 🎯 Features

The Multi-Purpose Business Application includes:

- **User Management**: Registration, login, and user profiles
- **Invoice Management**: Create, edit, and track invoices
- **Inventory Management**: Track products and stock levels
- **Client Management**: Manage customer information
- **Job Order Tracking**: Create and monitor job orders
- **Quotation System**: Generate and manage quotations
- **Receipt Management**: Track payments and receipts
- **Waybill System**: Manage shipping and delivery
- **Accounting**: Basic accounting and financial tracking

---

**Happy Business Management! 🚀**
