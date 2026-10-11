from uuid import UUID

from fastapi import APIRouter, status
from fastapi.responses import FileResponse

from app.api.deps import CurrentAdmin, DBSession
from app.schemas.document import DocumentMetadataResponse
from app.services.document import DocumentService

router = APIRouter()


@router.post(
    "/{application_id}/documents",
    response_model=DocumentMetadataResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_document(
    application_id: UUID,
    db: DBSession,
    admin: CurrentAdmin,
) -> DocumentMetadataResponse:
    document = await DocumentService(db).generate(application_id, admin)
    return DocumentMetadataResponse.model_validate(document)


@router.get(
    "/{application_id}/documents",
    response_model=list[DocumentMetadataResponse],
)
async def list_documents(
    application_id: UUID,
    db: DBSession,
    _admin: CurrentAdmin,
) -> list[DocumentMetadataResponse]:
    documents = await DocumentService(db).list_for_application(application_id)
    return [DocumentMetadataResponse.model_validate(item) for item in documents]


@router.get("/{application_id}/documents/{document_id}/download")
async def download_document(
    application_id: UUID,
    document_id: UUID,
    db: DBSession,
    _admin: CurrentAdmin,
) -> FileResponse:
    document, path = await DocumentService(db).get_for_download(
        application_id,
        document_id,
    )
    return FileResponse(
        path=path,
        media_type="application/pdf",
        filename=f"eduflow-demo-{document.id}.pdf",
        content_disposition_type="attachment",
    )
