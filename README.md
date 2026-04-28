<<<<<<< HEAD
# NetGuardViz

NetGuardViz is a security web application for analyzing system and network logs, detecting suspicious activity, and reviewing generated alerts. The backend uses FastAPI, MongoDB, and JWT-based authentication, while the frontend uses React and Vite for the dashboard UI.

## Features

- User signup and login with JWT authentication
- Role-aware authorization for protected routes
- Log upload, validation, and processing
- Suspicious keyword detection and alert generation
- Paginated and filterable logs and alerts views
- User-specific stats dashboard

## Tech Stack

- Backend: FastAPI, Pydantic, PyMongo, Python-JOSE, Passlib, Loguru
- Frontend: React, Vite, React Router, Axios
- Database: MongoDB

## Project Structure

```text
NetGuardViz/
├── app/
│   ├── api/
│   ├── auth/
│   ├── core/
│   ├── models/
│   ├── utils/
│   └── main.py
├── frontend/
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.10+ recommended
- Node.js 18+ recommended
- MongoDB running locally or remotely

## Environment Variables

Create a `.env` file in the project root with values like these:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=netguardviz_db

JWT_SECRET=your-secret-key
JWT_EXPIRE_MINUTES=5
ADMIN_EMAILS=admin@example.com,securitylead@example.com

SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@example.com
EMAIL_PASSWORD=your-app-password
TO_EMAIL=destination@example.com
```

## Backend Setup

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs at `http://127.0.0.1:8000`.

## Quick Project Summary

NetGuardViz is a full-stack log ingestion and analysis prototype intended for demonstration and learning. It provides:

- Secure JWT-based authentication and role-based access control (user/admin)
- Log upload and background processing for suspicious keyword detection
- Alert generation and admin controls for managing users and alerts
- Soft-delete for logs and role-aware APIs

## Recommended Pre-commit Checklist

Before publishing this repository or linking it publicly, ensure:

- No `.env` files or secrets are committed (use `.gitignore`) 
- `JWT_SECRET` is rotated and not the development default
- Database credentials are not stored in the repo

## How to Run (local)

1. Backend

```bash
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1    # Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. Frontend (separate terminal)

```bash
cd frontend
npm install
npm run dev
```

Open the frontend at `http://localhost:5173` and the API at `http://127.0.0.1:8000`.

## Admin/bootstrap notes

- The project supports an `ADMIN_EMAILS` environment variable (comma-separated). Any account that signs up using one of those emails is automatically granted the `admin` role on creation.
- After changing a user's role (or admin list), users must re-login to receive a JWT with the updated `role` claim.

## Security & Production Notes

- This project is a prototype. If you plan to deploy, consider:
	- Using HTTPS and secure secrets storage (Vault, environment, CI secrets)
	- Shortening JWT expiry and enabling refresh tokens
	- Enforcing stricter RBAC checks server-side (backend does, but review before production)

## Contributing & Contact

If you'd like me to help prepare a polished GitHub repo page, README screenshots, or a short demo video, tell me what you'd like included and I can add it.

## Frontend Setup

In a separate terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`.

## Main Routes

### Auth

- `POST /auth/signup` - create a new user
- `POST /auth/login` - authenticate and receive a JWT

### Logs

- `GET /api/logs/` - list the current user's logs
- `POST /api/logs/upload` - upload a new log file
- `PUT /api/logs/{log_id}` - update a log owned by the current user
- `DELETE /api/logs/{log_id}` - soft delete a log owned by the current user

### Alerts

- `GET /api/alerts/` - list the current user's alerts
- `DELETE /api/alerts/{alert_id}` - admin-only alert deletion

### Stats

- `GET /api/stats/` - return the current user's log and alert summary

## RBAC Summary

- `user`: can sign in, upload logs, and view their own logs, alerts, and stats
- `admin`: can perform privileged actions such as protected alert deletion and any other admin-only routes you add later

Authorization logic is split into:

- `app/auth/dependency.py` for `get_current_user`
- `app/auth/roles.py` for `require_role(...)`

## Notes

- The frontend uses `http://localhost:5173`, so CORS is already configured for that origin.
- Uploaded logs are processed asynchronously and may generate alerts if suspicious keywords are detected.
- If you add more admin routes later, keep `get_current_user` for identity checks and `require_role("admin")` for permission checks.
=======
# 🚀 NetGuardViz

**NetGuardViz** is a security-focused log analysis platform that ingests, processes, and monitors system logs to detect suspicious activity in real time. It converts raw logs into actionable alerts using automated pipelines, JWT authentication, and role-based access control.

---

## 🔥 Features

### 🛡️ Authentication & Security
- JWT-based authentication
- Role-Based Access Control (RBAC)
- Secure password hashing (bcrypt)

### 📂 Log Management
- Upload `.log`, `.txt`, `.json` files
- File validation (size, type, encoding)
- Background processing (non-blocking)

### 🚨 Threat Detection
- Keyword-based suspicious activity detection
- Automatic alert generation
- Alerts stored in MongoDB

### 📊 Data Handling
- Pagination for large datasets
- Filtering for logs and alerts
- Clean API responses

### 📢 Notifications
- Email alerts using SMTP

### 💻 Frontend
- React dashboard (Vite)
- Login with JWT storage
- Logs & Alerts table
- RBAC-based UI rendering

---

## 🏗️ Project Structure
NetGuardViz/
│
├── app/ # Backend (FastAPI)
│ ├── api/ # Routes (logs, alerts)
│ ├── auth/ # Auth (login, signup, RBAC)
│ ├── core/ # DB + security (JWT)
│ ├── models/ # Schemas
│ ├── utils/ # Detection logic
│ └── main.py # Entry point
│
├── frontend/ # React frontend (Vite)
│
├── services/ # External services (email, notifications)
│
├── .env # Environment variables (private)
├── .env.example # Sample env file
├── requirements.txt # Python dependencies
├── .gitignore
└── README.md

---

## ⚙️ Tech Stack

- Backend: FastAPI  
- Database: MongoDB  
- Auth: JWT (python-jose)  
- Hashing: Passlib + bcrypt  
- Frontend: React (Vite)  

---

## 🔐 Authentication Flow

1. User Signup → Store hashed password  
2. Login → Verify credentials  
3. Generate JWT Token  
4. Access protected APIs using token  
5. RBAC restricts access by role  

---

## 🚀 Getting Started


### 1. Clone Repo
git clone https://github.com/ASura12/NetGuardViz.git

cd NetGuardViz

### 2. Create Virtual Environment
python -m venv venv
source venv/bin/activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Setup Environment Variables
Create `.env` file:
MONGO_URI=your_mongodb_uri
SECRET_KEY=your_secret_key
ALGORITHM=HS256
EMAIL_USER=your_email
EMAIL_PASS=your_password

### 5. Run Server
uvicorn app.main:app --reload

---

## 📡 API Endpoints

### Auth
- POST `/auth/signup`
- POST `/auth/login`

### Logs
- POST `/api/logs/upload`
- GET `/api/logs?page=1&limit=20`

### Alerts
- GET `/api/alerts?page=1&limit=20`

---

## 🧠 Core Concepts

- Async background processing  
- JWT authentication  
- RBAC authorization  
- File validation pipeline  
- Alert generation system  

---

## 📌 Future Improvements

- Docker support  
- CI/CD pipeline  
- WebSocket real-time alerts  
- AI-based anomaly detection  

---

## 👨‍💻 Author

**Ashish Pathak**  
Cybersecurity | FastAPI | Backend Development
>>>>>>> 59c241b (Revise README to enhance project documentation)
