from uuid import UUID


class ApplicationNotFoundError(Exception):
    def __init__(self, application_id: UUID) -> None:
        self.application_id = application_id
        super().__init__(f"Application {application_id} not found")


class DocumentNotFoundError(Exception):
    def __init__(self, document_id: UUID) -> None:
        self.document_id = document_id
        super().__init__(f"Document {document_id} not found")


class DuplicatePhoneError(Exception):
    def __init__(self, phone: str) -> None:
        self.phone = phone
        super().__init__(f"An application with phone {phone} already exists")


class PdfGenerationError(Exception):
    def __init__(self, message: str = "Failed to generate PDF document") -> None:
        super().__init__(message)
