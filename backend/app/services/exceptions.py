from uuid import UUID

from app.models.enums import ApplicationStatus


class EduFlowError(Exception):
    """Base domain error."""


class NotFoundError(EduFlowError):
    pass


class TransitionError(EduFlowError):
    pass


class RequirementError(EduFlowError):
    pass


class AuthenticationError(EduFlowError):
    pass


class AuthorizationError(EduFlowError):
    pass


class ApplicationNotFoundError(NotFoundError):
    def __init__(self, application_id: UUID) -> None:
        super().__init__(f"Application {application_id} not found")


class InstitutionNotFoundError(NotFoundError):
    def __init__(self, institution_id: UUID) -> None:
        super().__init__(f"Institution {institution_id} not found")


class ProgramNotFoundError(NotFoundError):
    def __init__(self, program_id: UUID) -> None:
        super().__init__(f"Program {program_id} not found")


class RequirementProfileNotFoundError(NotFoundError):
    def __init__(self, profile_id: UUID) -> None:
        super().__init__(f"Requirement profile {profile_id} not found")


class TemplateDataError(EduFlowError):
    def __init__(self, message: str = "Required template data is missing") -> None:
        super().__init__(message)


class TemplateUnavailableError(EduFlowError):
    def __init__(self, message: str = "Document template is unavailable") -> None:
        super().__init__(message)


class PdfGenerationError(EduFlowError):
    def __init__(self, message: str = "Document generation failed") -> None:
        super().__init__(message)


class DocumentNotFoundError(NotFoundError):
    def __init__(self) -> None:
        super().__init__("Document not found")


class UnsafeStorageKeyError(EduFlowError):
    def __init__(self) -> None:
        super().__init__("Invalid document reference")


class InvalidTransitionError(TransitionError):
    def __init__(
        self,
        current: ApplicationStatus,
        target: ApplicationStatus,
    ) -> None:
        self.current = current
        self.target = target
        super().__init__(
            f"Cannot change application status from {current.value} to {target.value}"
        )
