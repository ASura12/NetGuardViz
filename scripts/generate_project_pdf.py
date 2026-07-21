from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Preformatted, PageBreak

OUTPUT_PATH = "docs/NetGuardViz_Project_Documentation.pdf"


def build_pdf() -> None:
    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="NetGuardViz Project Documentation",
        author="NetGuardViz Team",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        textColor=colors.HexColor("#0B3C5D"),
        fontSize=24,
        spaceAfter=14,
    )
    h1 = ParagraphStyle(
        "H1Custom",
        parent=styles["Heading1"],
        textColor=colors.HexColor("#1D3557"),
        fontSize=16,
        spaceBefore=10,
        spaceAfter=8,
    )
    body = ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontSize=10.5,
        leading=14,
        spaceAfter=6,
    )
    mono = ParagraphStyle(
        "MonoCustom",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8.6,
        leading=10.5,
    )

    content = []

    content.append(Paragraph("NetGuardViz", title_style))
    content.append(Paragraph("Comprehensive Project Documentation", styles["Heading3"]))
    content.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body))
    content.append(Spacer(1, 8))

    content.append(Paragraph("1. Project Overview", h1))
    content.append(
        Paragraph(
            "NetGuardViz is a full-stack security web application for analyzing system and network logs, "
            "detecting suspicious activity, and generating alerts. It is designed as a practical security-focused "
            "prototype that demonstrates authentication, role-based authorization, background processing, and "
            "admin operations in a single platform.",
            body,
        )
    )

    content.append(Paragraph("2. Core Features", h1))
    features = [
        "JWT-based authentication and protected routes",
        "Role-Based Access Control (user/admin)",
        "Log upload with file type, size, and content validation",
        "Background processing for suspicious keyword detection",
        "Alert generation and alert listing",
        "User-specific dashboard and stats views",
        "Admin user management (role/status updates)",
        "Soft-delete for logs",
    ]
    for item in features:
        content.append(Paragraph(f"- {item}", body))

    content.append(Paragraph("3. Technology Stack", h1))
    stack_table = Table(
        [
            ["Layer", "Technology"],
            ["Backend", "FastAPI, Pydantic, Python"],
            ["Database", "MongoDB (PyMongo)"],
            ["Authentication", "JWT (python-jose)"],
            ["Password Security", "passlib + bcrypt"],
            ["Frontend", "React + Vite + React Router"],
            ["Logging", "Loguru"],
        ],
        colWidths=[5.2 * cm, 10.2 * cm],
    )
    stack_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D3557")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    content.append(stack_table)

    content.append(Paragraph("4. System Architecture", h1))
    content.append(
        Paragraph(
            "The architecture follows a client-server model. The React frontend communicates with FastAPI endpoints. "
            "FastAPI handles auth, validation, role checks, and persistence to MongoDB. Log analysis runs in background tasks.",
            body,
        )
    )

    architecture_diagram = """
+--------------------------+        HTTP/JSON         +---------------------------+
|   React Frontend (Vite)  |  <-------------------->  |     FastAPI Backend       |
| - Login / Dashboard      |                          | - Auth Routes             |
| - Logs / Alerts / Admin  |                          | - Logs / Alerts / Stats   |
+------------+-------------+                          | - RBAC + JWT Validation   |
             |                                        | - Background Log Analysis |
             |                                        +-------------+-------------+
             |                                                      |
             |                                                      | PyMongo
             v                                                      v
                                     +-------------------------------+
                                     |           MongoDB             |
                                     | users, logs, alerts           |
                                     +-------------------------------+
"""
    content.append(Preformatted(architecture_diagram.strip("\n"), mono))

    content.append(Paragraph("5. Project Structure", h1))
    project_structure = """
NetGuardViz/
  app/
    api/
    auth/
    core/
    models/
    utils/
    main.py
  frontend/
    src/
    public/
    package.json
  services/
  requirements.txt
  README.md
"""
    content.append(Preformatted(project_structure.strip("\n"), mono))

    content.append(Paragraph("6. Key API Endpoints", h1))
    endpoints = [
        "POST /auth/signup - Create a new user",
        "POST /auth/login - Authenticate and return access token",
        "GET /api/logs/ - List user logs",
        "POST /api/logs/upload - Upload a log file",
        "DELETE /api/logs/{log_id} - Soft delete a log (owner or admin)",
        "GET /api/alerts/ - List user alerts",
        "DELETE /api/alerts/{alert_id} - Admin-only alert deletion",
        "GET /api/stats/ - User-specific dashboard statistics",
        "GET /auth/users - Admin-only user list",
        "PATCH /auth/users/{user_id}/role - Admin role update",
    ]
    for ep in endpoints:
        content.append(Paragraph(f"- {ep}", body))

    content.append(Paragraph("7. Authentication and Authorization", h1))
    auth_text = [
        "Authentication uses JWT bearer tokens.",
        "User identity is validated server-side in dependency checks.",
        "Role checks use RBAC helpers (for example, admin-only endpoints).",
        "Admin bootstrap is supported through ADMIN_EMAILS in environment configuration.",
        "After role changes, users should log out and log in again to receive updated token claims.",
    ]
    for line in auth_text:
        content.append(Paragraph(f"- {line}", body))

    content.append(Paragraph("8. Environment Configuration", h1))
    env_block = """
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=netguardviz_db
JWT_SECRET=your-secret-key
JWT_EXPIRE_MINUTES=60
ADMIN_EMAILS=admin@example.com,securitylead@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ADDRESS=your-email@example.com
EMAIL_PASSWORD=your-app-password
TO_EMAIL=destination@example.com
"""
    content.append(Preformatted(env_block.strip("\n"), mono))

    content.append(Paragraph("9. Local Setup", h1))
    backend_cmds = """
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
"""
    frontend_cmds = """
cd frontend
npm install
npm run dev
"""
    content.append(Paragraph("Backend commands:", body))
    content.append(Preformatted(backend_cmds.strip("\n"), mono))
    content.append(Paragraph("Frontend commands:", body))
    content.append(Preformatted(frontend_cmds.strip("\n"), mono))

    content.append(PageBreak())

    content.append(Paragraph("10. Security Notes", h1))
    security_notes = [
        "Never commit .env or secret values to source control.",
        "Use HTTPS in production environments.",
        "Rotate JWT secrets regularly.",
        "Add rate-limiting and stronger upload scanning for production workloads.",
        "Add centralized audit logs for admin actions.",
    ]
    for note in security_notes:
        content.append(Paragraph(f"- {note}", body))

    content.append(Paragraph("11. Future Updates / Roadmap", h1))
    roadmap = [
        "Replace simple background tasks with Celery/RQ workers and retries.",
        "Introduce test suites (pytest for backend, component/e2e tests for frontend).",
        "Add CI/CD pipeline with linting, tests, and build checks.",
        "Implement refresh token flow and session management hardening.",
        "Add advanced detection rules and configurable alert policies.",
        "Add WebSocket live updates for log and alert status changes.",
        "Containerize with Docker Compose and provide production deployment docs.",
        "Enhance observability with metrics and tracing.",
    ]
    for item in roadmap:
        content.append(Paragraph(f"- {item}", body))

    content.append(Paragraph("12. Resume / Portfolio Positioning", h1))
    content.append(
        Paragraph(
            "This project demonstrates end-to-end full-stack development, API design, RBAC security controls, "
            "data persistence, and practical debugging/change management. It is suitable as a portfolio project "
            "for backend, full-stack, or security-focused software roles.",
            body,
        )
    )

    doc.build(content)


if __name__ == "__main__":
    build_pdf()
