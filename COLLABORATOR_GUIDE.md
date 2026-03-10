# Quick Start Guide for Collaborators 

## 🏃‍♂️ Super Quick Setup (2 commands)

```bash
# 1. Run setup (one time only)
./setup.sh

# 2. Start the server (every time)
./start.sh
```

Then visit: **http://localhost:8000**

## 🔧 Configuration

1. **Copy credentials**: Your team lead should share the database credentials
2. **Update .env**: Replace the `YOUR_*` placeholders with actual values
3. **Connect VPN**: Make sure you're connected to company VPN

## 🛠️ Daily Development Workflow

```bash
# Activate environment
source .venv/bin/activate

# Start server for testing
python start_server.py

# Or use console chat for quick testing
python chat_with_database.py

# Test connectivity if having issues
python test_connectivity.py
```

## 📁 Key Files

- **`.env`** - Your database credentials (never commit this!)
- **`start_server.py`** - Web interface server
- **`chat_with_database.py`** - Console chat interface
- **`fundpilot_config.py`** - Core Vanna configuration

## 🤝 Collaboration Tips

1. **Always pull first**: `git pull origin main`
2. **Never commit .env**: Sensitive credentials stay local
3. **Test before push**: Run `python test_connection.py`
4. **Share connection strings securely**: Use encrypted chat/email

## 🆘 Common Issues

**"pyodbc not found"** → Run `./setup.sh` again

**"Login timeout expired"** → Check VPN connection & database server address

**"Driver not found"** → Install ODBC driver: `brew install msodbcsql18`

**"Port already in use"** → Kill existing server: `pkill -f start_server.py`

## 💡 Pro Tips

- Use `./start.sh` for quick server startup
- Keep your `.env` file backed up securely
- Test connectivity with `python test_connectivity.py` before debugging
- The web interface auto-refreshes when you ask new questions