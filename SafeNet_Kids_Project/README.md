# 🛡️ SafeNet Kids — AI-Powered Digital Protection

SafeNet Kids is a professional-grade child safety ecosystem that provides proactive monitoring, behavioral analytics, and remote parental intelligence. It leverages state-of-the-art AI to move beyond simple web filters, ensuring a safe digital environment for your family.

![SafeNet Dashboard](https://raw.githubusercontent.com/placeholder/safenet_dashboard.png)

## 🚀 Key Features

- **🧠 Multi-Layered AI Monitoring**:
  - **NLP Keystroke Analysis**: Detects intent and harmful language in real-time.
  - **Computer Vision OCR**: Scans screens for restricted text and application context.
  - **Deep Learning Image Moderation**: Automatically blocks inappropriate visual content.
- **📊 Intelligence Reporting**:
  - **Automated PDF Audits**: Daily, Weekly, and Monthly safety reports with charts.
  - **Risk Trends**: Tracks safety scores (0-100) and behavioral category distributions.
- **🛡️ Active Protection**:
  - **Process Blocker**: Instantly terminates restricted apps (Games, Unsafe Browsers).
  - **Smart Scheduling**: Set active monitoring hours for school or study time.
- **📧 Remote Alerts**:
  - **Instant Critical Alerts**: Real-time email notifications for high-risk activity.
  - **Cloud-Ready Notifications**: Desktop and email synchronization.

## 🛠️ Technology Stack

- **GUI**: CustomTkinter (Cyber-security themed)
- **AI**: TensorFlow, NLTK, Transformers (NLP)
- **Sensors**: Pytesseract (OCR), Pillow, PyGetWindow
- **Backend**: Python 3.11, SMTP_SSL
- **Reporting**: Matplotlib, ReportLab

## 📋 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Deepa0912/SafeNet_Kids_Project.git
   cd SafeNet_Kids_Project
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **External Requirements**:
   - Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) for screen scanning features.

4. **Run SafeNet**:
   ```bash
   python main.py
   ```

## 📦 Distribution

To package SafeNet as a standalone Windows executable, refer to our [Packaging Guide](docs/packaging_guide.md).

## 📄 Technical Documentation

For deep dives into architecture and AI methodology, see the [Technical Report](docs/technical_report.md).

---
*Created with ❤️ for a safer digital future.*
