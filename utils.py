"""
Utility functions module for Football Score Prediction application.
Contains helper functions used across the application.
"""
from datetime import datetime
from config import APP_TZ


def safe_float(val):
    """Safely convert value to float, return 0.0 on error"""
    try:
        return float(val)
    except:
        return 0.0


def normalize_status(status_value):
    """Normalize match status to standard format"""
    if not status_value:
        return "NS"
    status = str(status_value).lower()
    if status in ["finished", "ended", "ft"]:
        return "FT"
    if status in ["notstarted", "scheduled", "ns"]:
        return "NS"
    if status in ["inprogress", "live"]:
        return "LIVE"
    return status_value
