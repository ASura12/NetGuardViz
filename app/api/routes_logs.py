from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, Query
from app.core.database import logs_collection as logs_collection
from app.core.database import alerts_collection as alerts_collection
from app.models.log_model import LogModel
from app.models.schemas import all_tasks, LogUpdateModel
from app.auth.dependency import get_current_user
from app.auth.roles import require_role

import os
from bson import ObjectId
from fastapi import HTTPException
from pymongo.errors import PyMongoError
from app.core.logger import logger

router = APIRouter(prefix = "/api/logs", tags = ["Logs"])

@router.get("/")
async def get_logs(
    current_user=Depends(get_current_user),
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    suspicious: bool | None = None,
    filename: str | None = None
):

    query = {}
    query["is_deleted"] = {"$ne": True}
    query["owner_email"] = current_user["email"]

    if suspicious is not None:
        query["suspicious"] = suspicious

    if filename:
        query["filename"] = filename

    skip = (page - 1) * limit

    logs_raw = list(
        logs_collection
        .find(query)
        .skip(skip)
        .limit(limit)
    )

    # Transform logs to include id field
    logs = [
        {
            **{k: v for k, v in log.items() if k != "_id"},
            "id": str(log["_id"])
        }
        for log in logs_raw
    ]

    total = logs_collection.count_documents(query)

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "data": logs
    }

# CREATE logs --> Logs were created here and every users get log_id which will help them to read the logs
@router.post("/upload")
async def endpoint(
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_user),
    uploaded_file: UploadFile = File(...)
):

    # 1. Validate extension
    check_files_extension(uploaded_file.filename)

    # 2. Validate MIME type
    check_mime_type(uploaded_file.content_type)

    # 3. Read raw bytes
    content = await uploaded_file.read()

    # 4. Validate file size
    check_file_size(content)

    # 5. Decode safely
    text = read_file(content)

    # 6. Inspect if content is meaningful
    cleaned = validate_content_type(text)

    logger.info(f"File upload received: {uploaded_file.filename}")


    # 7. Save to DB
    log_id = logs_collection.insert_one({
        "owner_email": current_user["email"],
        "owner_id": current_user["id"],
        "filename": uploaded_file.filename,
        "content": cleaned,
        "uploaded_at": datetime.utcnow(),
        "status": "pending"
    }).inserted_id

    logger.info(f"Log stored in database: {log_id}")

    # 8. PUSH TASK TO BACKGROUND
    background_tasks.add_task(process_log_background, log_id)
    logger.warning(f"Suspicious log detected for log_id: {log_id}")

    # 9. RETURN immediately
    return {
        "message": "File uploaded. Analysis started.",
        "id": str(log_id)
    }


def check_files_extension(filename: str | None) -> str:
    file_extensions = [".log", ".txt", ".json"]

    if filename is None:
        raise HTTPException(status_code=400, detail="Missing filename")

    normalized_filename = filename.strip()
    if normalized_filename == "":
        raise HTTPException(status_code=400, detail="Missing filename")

    extension = os.path.splitext(normalized_filename)[1]
    ext = extension.lower()
    if ext == "" or ext == ".":
        raise HTTPException(status_code=400, detail="Invalid file format")
    if ext not in file_extensions:
        logger.error(f"Unsupported file format: {normalized_filename}")
        raise HTTPException(status_code=400, detail="Unsupported file Format")
    return ext

def process_log_background(log_id):

    # 1. Fetch the stored log
    log_record = logs_collection.find_one({"_id": log_id})
    if not log_record:
        logger.error(f"Log not found for processing: {log_id}")
        return

    # 2. Parse into lines
    lines = split_into_lines(log_record.get("content", ""))

    # 3. Keyword detection
    scan_for_suspicious_keywords(
        "\n".join(lines),
        logs_collection,
        alerts_collection,
        log_id,
        log_record.get("owner_email"),
        log_record.get("owner_id"),
        log_record.get("filename")
    )

    # 4. Mark as processed
    logs_collection.update_one(
        {"_id": log_id},
        {"$set": {"status": "processed"}}
    )


def split_into_lines(content: str) -> list[str]:
    if content is None:
        return []

    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    return [line for line in normalized.split("\n") if line.strip() != ""]


def check_mime_type(content_type):
    mime_list = ["text/plain", "text/x-log", "application/json"]

    if not content_type or content_type == "":
        raise HTTPException(status_code=400, detail = "Missing MIME Type")
    
    normalized = content_type.lower()

    if normalized not in  mime_list:
        raise HTTPException(status_code = 400, detail = "Unsupported MIME Type")
    return normalized

def check_file_size(content: bytes):
    MAX_SIZE = 5 * 1024 * 1024

    size = len(content)

    if size == 0:
        raise HTTPException(status_code=400, detail="Empty File")

    if size > MAX_SIZE:
        raise HTTPException(status_code=413, detail="Upload Too Large")

    return size

def read_file(content: bytes):
    if content is None:
        raise HTTPException(status_code=400, detail = "Missing file Content")
    try:
        text=content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code = 400, detail = "Invalid Encoding")
    text = text.replace("\r\n", "\n").replace("\r","\n")

    if "\x00" in text:
        raise HTTPException(status_code=400, detail="Binary or Corrupted File")
    
    return text

def validate_content_type(text):
    cleaned = text.strip()

    if cleaned == "":
        raise HTTPException(status_code=400, detail = "Empty file")
    lines = text.split("\n")
    meaningful_count = 0
    for line in lines:
        if line.strip() != "":
            meaningful_count+=1
    
    if meaningful_count == 0:
        raise HTTPException(status_code=400, detail="No meaningful Contetnt found")
    
    if meaningful_count < 2:
        raise HTTPException(status_code=400, detail = "File too empty to be a valid log")
    return cleaned

def save_log_to_db(collection, filename, cleaned_content):
    try:
        document = {
            "filename": filename,
            "content": cleaned_content,
            "uploaded_at": datetime.utcnow(),
            "suspicious": False    
        }

        result = collection.insert_one(document)

        if not result.inserted_id:
            raise HTTPException(
                status_code=500,
                detail="Database failed to store the log"
            )

        return {
            "message": "Log uploaded successfully",
            "log_id": str(result.inserted_id),
            "filename": filename
        }

    except PyMongoError:
        raise HTTPException(
            status_code=500,
            detail="Database error while inserting log"
        )

SUSPICIOUS_KEYWORDS = [
    "error",
    "failed",
    "unauthorized",
    "alert",
    "warning",
    "exception",
    "drop table",
    "select *",
    "shutdown",
    "hack",
    "attack"
]


def scan_for_suspicious_keywords(content, logs_collection, alerts_collection, log_id, owner_email, owner_id, filename):
    try:
        lower_content = content.lower()
        detected = []

        for keyword in SUSPICIOUS_KEYWORDS:
            if keyword in lower_content:
                detected.append(keyword)

        is_suspicious = len(detected) > 0

        # Update log record
        logs_collection.update_one(
            {"_id": log_id},
            {"$set": {"suspicious": is_suspicious,
                      "detected_keywords": detected}}
        )

        # If suspicious, store an alert
        if is_suspicious:
            alert_doc = {
                "log_id": log_id,
                "owner_email": owner_email,
                "owner_id": owner_id,
                "filename": filename,
                "detected_keywords": detected,
                "created_at": datetime.utcnow()
            }
            alerts_collection.insert_one(alert_doc)

        return {
            "suspicious": is_suspicious,
            "detected_keywords": detected
        }

    except PyMongoError:
        raise HTTPException(
            status_code=500,
            detail="Database error during suspicious scan"
        )





@router.put('/{log_id}')
async def update_log(log_id : str, update_data : LogModel, current_user=Depends(require_role("admin"))):
    # 1.Convert log_id str to ObjectId as MongoDb knows only about Object_Id
    try:
        obj_id = ObjectId(log_id)

    except Exception:
        raise HTTPException(status_code = 400, detail="Invalid Log Id")


    # 2. Convert update model to dict and remove None values
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}

    if not update_dict:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")

    # 3. Perform update
    result = logs_collection.update_one(
        {"_id": obj_id, "owner_email": current_user["email"], "is_deleted": {"$ne": True}},
        {"$set": update_dict}
    )

    # 4. Check if log exists
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Log not found")

    return {"message": "Log updated successfully"}

@router.delete('/{log_id}')
async def deleted_task(log_id: str, current_user=Depends(get_current_user)):
    try:
        obj_id = ObjectId(log_id)
    except Exception :
        raise HTTPException(status_code=400, detail = "Invalid Log ID") 
    
    # 2. Check if log exists
    existing_logs = logs_collection.find_one({
        "_id" : obj_id,
        "is_deleted" : {"$ne" : True}
    })

    if not existing_logs:
        raise HTTPException(status_code=404, detail="Log not found or already deleted")

    # 3. Check permissions: user can delete own logs, admin can delete any
    is_admin = current_user["role"] == "admin"
    is_owner = existing_logs["owner_email"] == current_user["email"]

    if not (is_admin or is_owner):
        raise HTTPException(status_code=403, detail="Access denied: can only delete your own logs")

    # 4. Perform soft delete
    logs_collection.update_one(
        {"_id": obj_id},
        {
            "$set": {
                "is_deleted": True,
                "deleted_at": datetime.utcnow()
            }
        }
    )

    return {"message": "Log soft deleted successfully"}

