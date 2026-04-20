from datetime import datetime
from app.core.database import logs_collection, alerts_collection
from app.utils.detector import detect_suspicious_keywords


def process_log_background(log_id):
    """
    Background processor:
    - fetches the saved log
    - runs suspicious keyword scan
    - inserts alerts
    - updates log status
    """

    # 1. Fetch stored log
    log_record = logs_collection.find_one({"_id": log_id})
    if not log_record:
        return  # nothing to process

    content = log_record.get("content", "")

    # 2. Perform detection
    result = detect_suspicious_keywords(
        log_record.get("filename", "unknown"),
        content
        
        
    )

    # 3. Mark log as processed
    logs_collection.update_one(
        {"_id": log_id},
        {"$set": {
            "status": "processed",
            "processed_at": datetime.utcnow()
        }}
    )

    return result
