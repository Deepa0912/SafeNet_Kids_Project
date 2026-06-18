# SafeNet Kids Project

A premium, intelligence-driven security dashboard and monitoring system for kids. Featuring real-time threat detection, computer vision content filtering, and process management, all wrapped in a professional cyber-security dark theme.

## ✨ New in v2.0
- **Modern Cyber-Security UI**: A complete 8-screen redesign with animated splash, integrated telemetry, and glassmorphic dashboards.
- **Advanced Auth**: Secure Parent/Admin account system with local encryption and master-key reset.
- **Live Intelligence Feed**: Real-time monitoring for NLP threats, keyboard activity, and visual content.
- **Enhanced Logging**: Searchable and filterable activity logs for full transparency.

## 📋 Prerequisites

- **Python 3.11**: Required for compatibility with TensorFlow 2.15. (Python 3.13 is NOT supported).
- **Operating System**: Windows (required for system-level monitoring).

## ⚙️ Setup Instructions

### 1. Navigate to the Project Folder
The project files are located in a sub-directory.

```powershell
cd d:\SafeNet_Kids_Project\SafeNet_Kids_Project
```

### 2. Configure the Environment
It is highly recommended to use a virtual environment.

```powershell
# Create a virtual environment using Python 3.11
py -3.11 -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. NLTK Data
The application downloads `vader_lexicon` automatically. If needed, run:
```powershell
python -c "import nltk; nltk.download('vader_lexicon')"
```

## 🚀 Running the Application

```powershell
python main.py
```

### 🔑 Authentication
On your first run, use the **Sign Up** tab to create your parent administrator account. You will need to set:
1. **Account Password**: For signing in.
2. **Parent Master Key**: A secondary password required to start/stop monitoring or modify security settings.

## 🛠️ Troubleshooting

- **Administrator Privileges**: Run your terminal as Administrator for key logging and process management features.
- **TensorFlow**: Ensure you have Microsoft Visual C++ Redistributable installed if TF fails to load.
