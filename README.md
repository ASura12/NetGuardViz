# 🚀 NetGuardViz

NetGuardViz is a full-stack security web application for analyzing system and network logs, detecting suspicious activity, and generating alerts.

It uses FastAPI (backend), MongoDB (database), and React + Vite (frontend).

---

## 🔥 Features

- JWT-based authentication  
- Role-Based Access Control (RBAC)  
- Log upload and validation  
- Background log processing  
- Suspicious keyword detection  
- Alert generation system  
- Admin role support  
- Dashboard with logs, alerts, and stats  

---

## 🏗️ Project Structure

NetGuardViz/
├── app/ (FastAPI backend)  
├── frontend/ (React frontend)  
├── requirements.txt  
└── README.md  

---

## ⚙️ Tech Stack

- Backend: FastAPI  
- Database: MongoDB  
- Auth: JWT  
- Frontend: React (Vite)  

---

## 🚀 Setup

### Backend
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
Frontend
cd frontend
npm install
npm run dev
```
### 📡 API
POST /auth/signup
POST /auth/login
POST /api/logs/upload
GET /api/logs
GET /api/alerts
### ⚠️ Notes
Do not commit .env
Rotate secrets before production
Use HTTPS in deployment
### 👨‍💻 Author

Ashish Pathak