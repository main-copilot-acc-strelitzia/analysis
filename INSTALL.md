# Installation & Setup Guide

## Minimum Requirements

- **Python**: 3.10 or newer
- **MetaTrader 5**: Terminal (Windows, Linux via Wine, or macOS via WineBottler)
- **OS**: Windows 7+, Debian/Ubuntu 18.04+, or macOS 10.12+
- **RAM**: 512 MB minimum (1 GB recommended)
- **Disk**: 50 MB free space

## Quick Install (2 minutes)

### 1. Verify Python Installation

```bash
python --version
# Output should be: Python 3.10 or higher
# If not installed, download from python.org
```

### 2. Install MetaTrader5 Package

```bash
pip install MetaTrader5
```

### 3. Start MetaTrader 5

- Open MetaTrader 5 on your computer
- Log in to your account
- Leave it running (the Python app connects to it)

### 4. Run Strelitzia Trader

```bash
cd path/to/strelitzia-server/mt5/trader
python main.py
```

That's it. The application will start immediately.

---

## Platform-Specific Installation

### Windows

**Prerequisites**
- Windows 7, 8, 10, 11, or Server Edition
- Python 3.10+ (download from python.org if needed)
- MetaTrader 5 (download from your broker)

**Installation Steps**

1. **Install Python**
   ```cmd
   # Download and run installer from python.org
   # Check "Add Python to PATH" during installation
   ```

2. **Verify Python**
   ```cmd
   python --version
   ```

3. **Install MetaTrader5 Package**
   ```cmd
   pip install MetaTrader5
   ```

4. **Install MetaTrader 5 Terminal**
   - Download from your broker's website
   - Run installer and log in

5. **Run Strelitzia Trader**
   ```cmd
   cd C:\path\to\strelitzia-server\mt5\trader
   python main.py
   ```

**Troubleshooting**
- If `python` command not recognized: Add Python to PATH
- If MT5 connection fails: Ensure MT5 is running and logged in
- If "MetaTrader5 module not found": Run `pip install --upgrade MetaTrader5`

---

### Linux (Debian/Ubuntu)

**Prerequisites**
- Debian 9+, Ubuntu 18.04+, or equivalent
- Python 3.10+
- Wine (to run MetaTrader 5)

**Installation Steps**

1. **Install Python**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   python3 --version
   ```

2. **Install Wine**
   ```bash
   # For 32-bit and 64-bit support
   sudo apt install wine wine32 wine64
   winearch
   wine --version
   ```

3. **Install MetaTrader5 Package**
   ```bash
   pip3 install MetaTrader5
   ```

4. **Install MetaTrader 5 via Wine**
   ```bash
   # Download MT5 setup from your broker
   # Run with Wine
   wine path/to/mt5setup.exe
   
   # Or use pre-configured Wine container
   # (Varies by broker - follow broker instructions)
   ```

5. **Configure Wine for MT5**
   ```bash
   # Ensure MT5 starts automatically or persistently
   # May need to configure Wine prefix for proper operation
   WINEPREFIX=~/.wine wine ~/.wine/drive_c/Program\ Files/MetaTrader\ 5/terminal.exe
   ```

6. **Run Strelitzia Trader**
   ```bash
   cd path/to/strelitzia-server/mt5/trader
   python3 main.py
   ```

**Troubleshooting**
- If Wine not installed: `sudo apt install wine wine32 wine64`
- If MT5 won't connect: Ensure Wine MT5 is fully installed and running
- If permissions denied: `chmod +x` the trader directory
- If Python packages fail: `pip3 install --user MetaTrader5`

---

### macOS

**Prerequisites**
- macOS 10.12 (Sierra) or newer
- Python 3.10+
- WineBottler or Parallels Desktop or similar

**Installation Steps**

1. **Install Python**
   ```bash
   # Using Homebrew (recommended)
   brew install python@3.10
   python3 --version
   
   # Or download from python.org
   ```

2. **Install WineBottler (or similar)**
   ```bash
   # Download from: bottler.kronenberg.org
   # Or use Parallels Desktop, VMware Fusion, etc.
   ```

3. **Install MetaTrader5 Package**
   ```bash
   pip3 install MetaTrader5
   ```

4. **Install MetaTrader 5 via WineBottler**
   - Download MT5 installer from your broker
   - Use WineBottler to create MT5 bottle
   - Install MT5 in the bottle
   - Configure to run on startup

5. **Ensure MT5 Runs in WineBottler**
   - Start WineBottler MT5 bottle before running Python app
   - Or configure WineBottler to auto-start

6. **Run Strelitzia Trader**
   ```bash
   cd path/to/strelitzia-server/mt5/trader
   python3 main.py
   ```

**Troubleshooting**
- If Python not found: `brew install python3` or adjust PATH
- If MT5 in WineBottler won't connect: Check WineBottler configuration
- If MetaTrader5 package fails: `pip3 install --upgrade pip setuptools` first
- For M1/M2 Macs: Some Wine alternatives may be needed

---

## Optional: Additional Packages

For enhanced functionality, install optional packages:

```bash
pip install psutil python-dateutil
```

**What They Do:**
- `psutil`: Better system monitoring and process detection
- `python-dateutil`: Enhanced date/time handling

---

## Verification

After installation, verify everything works:

```bash
# 1. Verify Python
python --version
# Should output: Python 3.x.x

# 2. Verify MetaTrader5 package
python -c "import MetaTrader5; print('MetaTrader5 OK')"
# Should output: MetaTrader5 OK

# 3. Verify application structure
cd path/to/strelitzia-server/mt5/trader
ls -la main.py
# Should show main.py exists

# 4. Verify MT5 is accessible
# Open MetaTrader 5 and log in
# Leave it running

# 5. Run application
python main.py
# Should start the Strelitzia Trader interface
```

---

## Upgrade Instructions

### Upgrade MetaTrader5 Package

```bash
pip install --upgrade MetaTrader5
```

### Upgrade Application Code

```bash
cd path/to/strelitzia-server/mt5/trader
git pull origin main
```

---

## Troubleshooting Installation

### Python Issues

**Problem**: `python: command not found`
```bash
# Solution 1: Use python3 instead
python3 main.py

# Solution 2: Add Python to PATH (Windows)
# Check "Add Python to PATH" during reinstall

# Solution 3: Use full path
/usr/bin/python3 main.py
```

**Problem**: `ModuleNotFoundError: No module named 'MetaTrader5'`
```bash
# Solution: Install the package
pip install MetaTrader5
# Or if using Python 3
pip3 install MetaTrader5
```

### MetaTrader 5 Issues

**Problem**: `Cannot connect to MetaTrader 5`
```
1. Ensure MetaTrader 5 terminal is open
2. Ensure your account is logged in
3. On Linux/Mac: Ensure Wine/WineBottler MT5 is running
4. Restart MT5 and try again
5. Check MT5 network settings
```

**Problem**: `MetaTrader 5 not found` (Linux/Mac)
```bash
# On Linux with Wine
export WINEARCH=win32
wine ~/.wine/drive_c/Program\ Files/MetaTrader\ 5/terminal.exe

# On Mac with WineBottler
# Use WineBottler GUI to configure MT5 bottle
# Ensure boot camp or virtual machine is configured
```

### Permission Issues

**Problem**: `Permission denied` (Linux/Mac)
```bash
# Solution: Check directory permissions
ls -la trader/
# Should show read/execute permissions

# If needed, fix permissions
chmod 755 trader/
chmod 644 trader/*.py
```

### Performance Issues

**Problem**: Slow analysis or high CPU usage
```
1. Reduce number of symbols analyzed simultaneously
2. Use 'fast' analysis mode instead of 'deep'
3. Increase timeframe interval (H1 instead of M5)
4. Check available RAM: `free -h` (Linux) or Activity Monitor (Mac)
5. Close other applications consuming resources
```

---

## Configuration Files

### Default Locations

- **Windows**: `C:\Users\[User]\strelitzia-server\mt5\trader\config\settings.py`
- **Linux**: `~/strelitzia-server/mt5/trader/config/settings.py`
- **macOS**: `~/strelitzia-server/mt5/trader/config/settings.py`

### Key Settings

Edit `config/settings.py` to customize:

```python
ANALYSIS_CONFIG = {
    'analysis_depth': 'standard',    # 'fast', 'standard', or 'deep'
    'timeframes': ['M5', 'H1', 'D1'],  # Default timeframes
    'max_symbols': 10,                 # Concurrent symbols
    'cache_expiry': 300,               # Cache duration (seconds)
    'include_explanations': True,      # Show signal explanations
    'explanation_verbosity': 'concise'  # 'concise' or 'detailed'
}
```

---

## Docker (Optional)

For containerized deployment:

```bash
# Build Docker image
docker build -t strelitzia:latest .

# Run container
docker run --network host strelitzia:latest

# Or with mounted volume
docker run --network host -v /path/to/trader:/app strelitzia:latest
```

Note: Requires proper Docker setup for MT5 integration.

---

## Uninstall

To remove Strelitzia Trader:

```bash
# Remove Python package
pip uninstall MetaTrader5

# Remove application directory
rm -rf path/to/strelitzia-server/mt5/trader

# Optional: Remove optional packages
pip uninstall psutil python-dateutil
```

---

## Support

If installation fails:

1. **Verify Python version**: `python --version` (needs 3.10+)
2. **Check MetaTrader 5**: Ensure terminal is running and logged in
3. **Check network**: Ensure system can connect to MT5 (usually local)
4. **Check disk space**: Need at least 50 MB free
5. **Check permissions**: Ensure read/write access to trader directory
6. **Check logs**: Application logs appear in console output

For platform-specific issues, refer to your OS documentation or contact your MetaTrader 5 broker support.

---

## What's Next?

After installation:

1. **Read** [README.md](README.md) for full feature overview
2. **Run** `python main.py` to start analysis
3. **Select** your preferred symbols and timeframes
4. **Monitor** real-time confluence scores

Happy trading!

---

**Last Updated**: December 27, 2025  
**Version**: 1.0.0  
**Status**: Production Ready
