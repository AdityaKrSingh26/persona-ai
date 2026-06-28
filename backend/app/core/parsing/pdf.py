import httpx
import fitz  # PyMuPDF


def _parse_bytes(pdf_bytes: bytes) -> str:
    # "text" mode preserves reading order; "blocks" or "dict" would need extra reassembly
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        pages = [page.get_text("text") for page in doc]
        # Double newline between pages mirrors paragraph boundaries for the chunker
        text = "\n\n".join(pages).strip()
    finally:
        doc.close()

    if not text:
        raise ValueError("PDF appears to be a scanned image — no extractable text found")

    return text


async def extract_pdf_from_url(url: str) -> str:
    """Download a PDF from a URL (e.g. Cloudinary) and extract text."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
    return _parse_bytes(response.content)
