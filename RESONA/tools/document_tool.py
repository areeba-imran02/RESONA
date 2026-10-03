"""
RESONA - Document Reader Tool

Reads supported emergency-response documents and extracts
their text for downstream agent analysis.

Supported formats:
- PDF
- TXT
"""

from pathlib import Path
from typing import Dict, List, Optional

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
}


class DocumentReadError(Exception):
    """Raised when a document cannot be read safely."""


def _validate_file_path(
    file_path: str,
) -> Path:
    """
    Validate that the provided path points to a supported
    file type.
    """

    if not file_path or not file_path.strip():
        raise DocumentReadError(
            "Document path cannot be empty."
        )

    path = Path(file_path)

    if not path.exists():
        raise DocumentReadError(
            f"Document not found: {file_path}"
        )

    if not path.is_file():
        raise DocumentReadError(
            f"Provided path is not a file: {file_path}"
        )

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise DocumentReadError(
            "Unsupported document type. "
            "Supported formats: PDF and TXT."
        )

    return path


def read_text_file(
    file_path: str,
) -> str:
    """
    Read a plain-text document using UTF-8 encoding.

    A replacement strategy is used for unusual characters
    so that one malformed character does not break the
    entire emergency workflow.
    """

    path = _validate_file_path(file_path)

    if path.suffix.lower() != ".txt":
        raise DocumentReadError(
            "read_text_file only accepts TXT files."
        )

    try:
        return path.read_text(
            encoding="utf-8",
            errors="replace",
        ).strip()

    except OSError as exc:
        raise DocumentReadError(
            f"Unable to read TXT document: {exc}"
        ) from exc


def read_pdf_file(
    file_path: str,
) -> Dict[str, object]:
    """
    Extract text from every page of a PDF.

    Returns both combined text and page-level text so that
    downstream systems can preserve page context.
    """

    path = _validate_file_path(file_path)

    if path.suffix.lower() != ".pdf":
        raise DocumentReadError(
            "read_pdf_file only accepts PDF files."
        )

    try:
        reader = PdfReader(str(path))

    except Exception as exc:
        raise DocumentReadError(
            f"Unable to open PDF document: {exc}"
        ) from exc

    pages: List[Dict[str, object]] = []
    combined_parts: List[str] = []

    for page_number, page in enumerate(
        reader.pages,
        start=1,
    ):

        try:
            text = page.extract_text() or ""

        except Exception as exc:
            text = (
                f"[Page {page_number} could not be "
                f"fully extracted: {exc}]"
            )

        text = text.strip()

        page_record = {
            "page": page_number,
            "text": text,
        }

        pages.append(page_record)

        if text:
            combined_parts.append(
                f"[Page {page_number}]\n{text}"
            )

    combined_text = "\n\n".join(
        combined_parts
    ).strip()

    return {
        "file_name": path.name,
        "file_type": "pdf",
        "page_count": len(reader.pages),
        "text": combined_text,
        "pages": pages,
    }


def read_document(
    file_path: str,
) -> Dict[str, object]:
    """
    Read a supported document and return structured content.
    """

    path = _validate_file_path(file_path)

    extension = path.suffix.lower()

    if extension == ".txt":

        text = read_text_file(
            str(path)
        )

        return {
            "file_name": path.name,
            "file_type": "txt",
            "page_count": 1,
            "text": text,
            "pages": [
                {
                    "page": 1,
                    "text": text,
                }
            ],
        }

    if extension == ".pdf":
        return read_pdf_file(
            str(path)
        )

    raise DocumentReadError(
        "Unsupported document type."
    )


def read_documents(
    file_paths: List[str],
) -> Dict[str, object]:
    """
    Read multiple supported documents.

    Individual document failures are returned as errors
    instead of stopping all other documents from being read.
    """

    if not file_paths:
        return {
            "documents": [],
            "successful": 0,
            "failed": 0,
            "errors": [],
        }

    documents = []
    errors = []

    for file_path in file_paths:

        try:
            document = read_document(
                file_path
            )

            documents.append(
                document
            )

        except DocumentReadError as exc:

            errors.append(
                {
                    "file": str(file_path),
                    "error": str(exc),
                }
            )

    return {
        "documents": documents,
        "successful": len(documents),
        "failed": len(errors),
        "errors": errors,
    }


def build_document_context(
    documents: List[Dict[str, object]],
    max_characters: int = 30000,
) -> str:
    """
    Convert extracted documents into a compact context block
    suitable for passing into the agent workflow.

    The limit prevents very large documents from unnecessarily
    expanding the LLM context.
    """

    if not documents:
        return ""

    max_characters = max(
        int(max_characters),
        1000,
    )

    sections: List[str] = []
    current_length = 0

    for document in documents:

        file_name = str(
            document.get(
                "file_name",
                "Unknown document",
            )
        )

        text = str(
            document.get(
                "text",
                "",
            )
        ).strip()

        if not text:
            continue

        section = (
            f"DOCUMENT: {file_name}\n"
            f"{text}"
        )

        remaining = (
            max_characters
            - current_length
        )

        if remaining <= 0:
            break

        if len(section) > remaining:
            section = section[
                :remaining
            ]

            section += (
                "\n[Document context truncated]"
            )

        sections.append(section)

        current_length += len(section)

    return "\n\n---\n\n".join(
        sections
    )


def get_document_tools() -> Dict[str, callable]:
    """
    Return document-reading functions in a simple registry.
    """

    return {
        "read_document": read_document,
        "read_documents": read_documents,
        "build_document_context": (
            build_document_context
        ),
    }
