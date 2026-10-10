import enum


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"


class ApplicationStatus(str, enum.Enum):
    NEW = "NEW"
    PENDING_REVIEW = "PENDING_REVIEW"
    CONTRACT_GENERATED = "CONTRACT_GENERATED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class DocumentType(str, enum.Enum):
    QUESTIONNAIRE = "QUESTIONNAIRE"
    CONTRACT = "CONTRACT"
