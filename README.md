# WebDAV Service Manager

A lightweight WebDAV service management tool based on Python + PySide6, providing a visual configuration interface with cross-platform support.

![Screenshot](assets/2026-03-02-13-19-07-image.png)

## Features

- [x] **Pure Visual Operation** - No command-line configuration required, all features accessible via GUI
- [x] **Configuration Validation** - Strict validation mechanism, invalid configurations cannot be applied
- [x] **Toast Notifications** - Windows-style notification system
- [x] **System Tray Support** - Minimize to system tray for convenient access
- [x] **Cross-Platform** - Supports Windows, Linux, and macOS
- [x] **Secure Authentication** - Username/password access control
- [x] **Comprehensive Logging** - Complete operation and error logging
- [x] **Client Compatibility** - Supports various clients (Android, Windows, Linux)

## System Requirements

- Python 3.7 or higher
- Supported OS: Windows 10+, Linux, macOS
- At least 100MB free disk space

## Installation

### 1. Clone or Download the Project

```bash
# Create project directory
mkdir webdav_manager
cd webdav_manager
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install PySide6 wsgidav cheroot
```

### 3. Run the Program

```bash
python main.py
```

## Usage Guide

### First Time Setup

1. **Start the Program**

   - Run `python main.py`
   - The program will automatically create a `./data` directory for configuration and logs

2. **Configure the Service**

   - **Share Directory**: Click "Browse" to select the folder to share
   - **Service Port**: Set the service port (recommended 8088-8099, range 1025-65535)
   - **Username**: Set the login username
   - **Password**: Set the login password

3. **Apply Configuration**

   - Click "Apply Config" button
   - The program will automatically validate the configuration
   - Valid configurations are saved to `./data/config.json`

4. **Start the Service**

   - Click "Start Service" button
   - Wait for "Service started" notification
   - The interface will display the running status

5. **Get Access URL**

   - Click "Copy Access URL" button
   - Access URL format: `http://[YOUR_IP]:[PORT]/`

### Client Connection

#### Android Clients

Recommended apps:

- **ES File Explorer**
- **Solid Explorer**
- **FX File Explorer**

Connection steps:

1. Open the app's network feature
2. Add WebDAV connection
3. Enter server address, username, and password
4. Access files after successful connection

#### Windows Clients

**Method 1: Map Network Drive**

1. Open "This PC"
2. Click "Map network drive"
3. Enter address: `http://[SERVER_IP]:[PORT]/`
4. Enter username and password
5. Complete the mapping

**Method 2: Direct Access via File Explorer**

1. In the address bar, enter: `\\[SERVER_IP]@[PORT]\DavWWWRoot`
2. Enter username and password

#### Linux Clients

**Method 1: Using davfs2**

```bash
sudo apt-get install davfs2
sudo mount -t davfs http://[SERVER_IP]:[PORT]/ /mnt/webdav
```

**Method 2: Using File Manager**

- Nautilus (GNOME): Files → Connect to Server
- Dolphin (KDE): Network → Add Network Folder

### Get Local IP Address

#### Windows

```cmd
ipconfig
```

Look for the IPv4 address

#### Linux/macOS

```bash
ip addr
# or
ifconfig
```

## Configuration File

Configuration file location: `./data/config.json`

```json
{
    "share_dir": "/path/to/share",
    "port": 8088,
    "username": "admin",
    "password": "password",
    "last_update": "2024-01-01 12:00:00"
}
```

## Log File

Log file location: `./data/webdav.log`

Log content includes:

- Program startup and shutdown
- Configuration changes
- Service start/stop events
- Errors and warnings

You can open the log file via the "View Log" button in the interface.

## Project Structure

```
webdav_manager/
├── main.py                    # Main program entry
└── manager/
    ├── ui_manager.py          # UI interface management
    ├── config_manager.py      # Configuration management
    ├── service_manager.py     # Service management
    ├── notification_manager.py # Notification management
    └── tray_manager.py        # System tray management
├── requirements.txt          # Dependencies list
├── README.md                 # Documentation
├── assets/
│   └── icon.ico             # Application icon
└── data/                     # Data directory (auto-created)
    ├── config.json          # Configuration file
    └── webdav.log           # Runtime log
```

## FAQ

### Q1: What if the port is already in use?

**A:** Change the port number in the configuration, avoid commonly used ports like 80, 443, 8080. Recommended port range: 8088-8099.

### Q2: Client connection failed?

**A:**

- Check firewall settings to ensure the port is open
- Verify client and server are on the same network
- Confirm IP address and port are correct
- Check username and password

### Q3: Cannot write to directory?

**A:** Check read/write permissions for the shared directory, ensure the program has access. On Windows, you may need to run as administrator.

### Q4: How to view runtime logs?

**A:** Click the "View Log" button in the interface, or directly open the `./data/webdav.log` file.

### Q5: Does it support external network access?

**A:** This tool is designed for internal network environments. For external access, you need:

- Configure router port forwarding
- Set firewall rules
- Consider security (recommended use VPN)

### Q6: Low ports (below 1024) cannot be used?

**A:**

- Windows: Requires administrator privileges
- Linux: Requires root privileges or use ports above 1025

### Q7: Configuration file corrupted?

**A:** The program will automatically detect and reset to default configuration, just reconfigure.

## Performance Optimization Tips

1. **When sharing many files**

   - Recommended to use SSD
   - Organize directory structure reasonably
   - Avoid excessively deep directory hierarchies

2. **Multi-client concurrent access**

   - Ensure server has sufficient bandwidth
   - Monitor system resource usage

3. **Long-term operation**

   - Regularly check log file size
   - Clean up log files if necessary

## Security Recommendations

1. **Use strong passwords**

   - Use complex usernames and passwords
   - Change passwords regularly

2. **Internal network use only**

   - Use only in trusted network environments
   - Avoid direct exposure to the public internet

3. **Permission control**

   - Only share necessary directories
   - Regularly check shared directory content

4. **Firewall configuration**

   - Only allow trusted IP access
   - Restrict port access range

## Packaging for Release

Use PyInstaller to package into standalone executable:

### Windows

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name WebDAV-Manager --icon=assets/icon.ico main.py
```

### Linux

```bash
pip install pyinstaller
pyinstaller --onefile --name webdav-manager main.py
```

The generated executable will be in the `dist` directory.

## Technical Support

If you encounter issues, please:

1. Check the log file `./data/webdav.log`
2. Review the configuration file `./data/config.json`
3. Refer to the FAQ section in this document

## Changelog

### v1.0.0 (2024-12-30)

- Initial release
- Implemented basic WebDAV service functionality
- Provided visual configuration interface
- Supported cross-platform operation
- Toast notification system
- Complete logging
- System tray integration

## License

This project is for learning and personal use only.

[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)

## Acknowledgments

- [WsgiDAV](https://github.com/mar10/wsgidav) - WebDAV service implementation
- [PySide6](https://wiki.qt.io/Qt_for_Python) - Qt interface framework
- [Cheroot](https://github.com/cherrypy/cheroot) - WSGI server

---

**Enjoy your file sharing experience!** 🚀
