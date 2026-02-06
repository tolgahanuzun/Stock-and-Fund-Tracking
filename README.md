# Stock & Fund Tracking Application

A simple, lightweight web application for tracking stock and fund portfolios.

[🇹🇷 Türkçe README](README_TR.md)

## Screenshots

| Dashboard (Index) | Admin Panel |
|:---:|:---:|
| <img src="img/index.png" alt="Dashboard" width="400"/> | <img src="img/admin.png" alt="Admin Panel" width="400"/> |

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite, APScheduler
- **Frontend:** HTML, CSS (Bootstrap), Vanilla JavaScript
- **Data Source:** TEFAS (via crawler)

## Key Features

- **Asset Management:** Add/Edit funds and stocks via Admin panel.
- **Portfolio Tracking:** Track quantity, cost, and current value.
- **Automated Data:** Daily price updates from TEFAS background jobs.
- **Charts:** Historical price visualization with Chart.js.
- **Multi-language:** English and Turkish support (Frontend & Admin).

## Installation

1. **Clone & Setup:**
   ```bash
   git clone <repo-url>
   cd borsa-takip
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run:**
   ```bash
   uvicorn backend.main:app --reload
   ```

3. **Access:**
   - App: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - Admin: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)

## Todo List

- [ ] Mobile App (React Native/Flutter)
- [ ] Telegram Bot Notifications
- [ ] User Authentication (JWT)
- [ ] Foreign Stocks & Crypto Support
- [ ] Data Export (CSV/Excel)
