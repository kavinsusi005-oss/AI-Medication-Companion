# 💊 MedMate - AI-Powered Medication Companion

> **Your medicine. Your routine. Your mate.**

A voice-first, zero-learning Progressive Web Application (PWA) designed for senior citizens and their caregivers. MedMate communicates naturally via voice in Tamil, English, and Tanglish, adapts to seniors without complex menus, and allows caregivers to manage schedules and monitor adherence in real-time.

---

## ✨ Features

- 🎙️ **Voice-First AI Interface**: Built with Web Speech API & Google Gemini 2.0 Flash for multi-language natural voice interactions.
- 🌐 **Per-Message Language Detection**: Speaks and understands **Tamil (தமிழ்)**, **English**, and **Tanglish** dynamically.
- 📅 **Schedule & Daily Dose Timeline**: Visual daily medication slots (`Morning`, `Afternoon`, `Evening`, `Night`) with interactive `Mark Taken` buttons that prevent double-dosing.
- 📊 **Monthly Adherence Tracker**: Calendar grid with compliance status micro-dots (`🟢 Taken`, `🟡 Pending`, `🔴 Missed`).
- 👤 **Patient & Caregiver Profiles**: Manage doctor details, emergency phone numbers, and language preferences.
- ⚙️ **Caregiver Admin Dashboard**: Add/edit prescribed medications, inspect real-time schedule compliance, and trigger demo simulations.
- 📱 **Progressive Web App (PWA)**: Installable directly onto Android and iOS home screens with offline caching via Service Workers.

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                       MEDMATE PWA                           │
│  [ 🎙️ Voice ]   [ 📅 Calendar ]   [ 👤 Profile ]   [ ⚙️ Admin ] │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON API
┌──────────────────────────────▼──────────────────────────────┐
│                    FASTAPI BACKEND                          │
│  ┌──────────────────┐  ┌────────────────┐  ┌─────────────┐  │
│  │ MedicationRoutes │  │InteractRoutes  │  │ AdminRoutes │  │
│  └─────────┬────────┘  └────────┬───────┘  └──────┬──────┘  │
│  ┌─────────▼────────────────────▼─────────────────▼──────┐  │
│  │                     SERVICES                          │  │
│  │  ┌──────────────┐  ┌─────────────────┐  ┌──────────┐  │  │
│  │  │ AI / NLU     │  │ Medication Svc  │  │Scheduler │  │  │
│  │  └──────┬───────┘  └────────┬────────┘  └──────────┘  │  │
│  └─────────┼───────────────────┼─────────────────────────┘  │
│     ┌──────▼──────┐     ┌──────▼──────┐                     │
│     │ Gemini API  │     │   SQLite    │                     │
│     └─────────────┘     └─────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. Seed Demo Data
```bash
python -m backend.seed_data
```

### 3. Run the Server
```bash
python -m backend.app
```

Open **`http://localhost:8000`** on your browser or **`http://<YOUR_WIFI_IP>:8000`** on your mobile phone.

---

## 🧪 Running Tests
```bash
python -m unittest tests/test_basic.py
```
