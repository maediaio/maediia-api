"""SQLAlchemy models."""
# Import leaf models first (no relationships to other models)
from app.models.user import User
from app.models.phone_number import PhoneNumber
from app.models.lead import Lead
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.scheduled_task import ScheduledTask
from app.models.api_key import ApiKey
from app.models.audit_log import AuditLog

# Import models that depend on leaf models (order matters!)
from app.models.call_log import CallLog
from app.models.sms_log import SmsLog
from app.models.voicemail import Voicemail  # Must be before BusinessLine
from app.models.business_line import BusinessLine  # Depends on Voicemail

# Import Agent (depends on CallLog)
from app.models.agent import Agent

# Import Organization last (depends on everything)
from app.models.organization import Organization

__all__ = [
    "User",
    "PhoneNumber",
    "Lead",
    "Service",
    "Appointment",
    "ScheduledTask",
    "ApiKey",
    "AuditLog",
    "CallLog",
    "SmsLog",
    "Voicemail",
    "BusinessLine",
    "Agent",
    "Organization",
]
