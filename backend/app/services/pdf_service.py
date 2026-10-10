import asyncio
from datetime import UTC, date, datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.models.application import Application
from app.services.exceptions import PdfGenerationError

BACKEND_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = BACKEND_ROOT / "app" / "templates"
DOCUMENTS_DIR = BACKEND_ROOT / "storage" / "documents"
CONTRACT_TEMPLATE = "contract_template.html"

_jinja_env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"]),
)


def _format_date(value: date | datetime | str) -> str:
    if isinstance(value, (date, datetime)):
        return value.strftime("%d %B %Y")
    return str(value)


def delete_generated_file(file_path: str) -> None:
    path = Path(file_path)
    if not path.is_absolute():
        path = BACKEND_ROOT / path
    path.unlink(missing_ok=True)


def _render_contract_html(application: Application) -> str:
    template = _jinja_env.get_template(CONTRACT_TEMPLATE)
    return template.render(
        applicant_name=application.applicant_name,
        birth_date=_format_date(application.birth_date),
        phone=application.phone,
        course_name=application.course_name,
        current_date=_format_date(datetime.now(UTC).date()),
    )


def _write_pdf(html: str, output_path: Path) -> None:
    HTML(string=html, base_url=str(TEMPLATES_DIR)).write_pdf(target=str(output_path))


async def generate_contract_pdf(application: Application) -> str:
    """Render the contract template and write a PDF. Returns a relative file path."""
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S")
    filename = f"contract_{application.id}_{timestamp}.pdf"
    output_path = DOCUMENTS_DIR / filename
    relative_path = str(output_path.relative_to(BACKEND_ROOT))

    try:
        html = _render_contract_html(application)
        await asyncio.to_thread(_write_pdf, html, output_path)
    except Exception as exc:
        if output_path.exists():
            output_path.unlink(missing_ok=True)
        raise PdfGenerationError(
            "Failed to generate the training contract PDF."
        ) from exc

    if not output_path.is_file() or output_path.stat().st_size == 0:
        output_path.unlink(missing_ok=True)
        raise PdfGenerationError("Generated contract PDF is empty or missing.")

    return relative_path
