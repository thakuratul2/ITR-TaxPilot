"""Table extraction module for Form 16 Part A and Part B tables."""

import fitz  # PyMuPDF

from app.documents.models import ExtractedTable


def extract_tables_from_page(page: fitz.Page, page_number: int) -> list[ExtractedTable]:
    """Extract structured tabular data from a PDF page using PyMuPDF table finder."""
    extracted_tables: list[ExtractedTable] = []

    try:
        tabs = page.find_tables()
        for tab in tabs:
            df_rows = tab.extract()
            if df_rows and len(df_rows) > 0:
                # Clean headers and rows
                raw_header = df_rows[0]
                headers = [str(col).strip() if col is not None else "" for col in raw_header]
                data_rows: list[list[str]] = []
                for row in df_rows[1:]:
                    cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                    # Only add if row is not completely empty
                    if any(cleaned_row):
                        data_rows.append(cleaned_row)

                if headers or data_rows:
                    extracted_tables.append(
                        ExtractedTable(
                            page_number=page_number,
                            headers=headers,
                            rows=data_rows,
                        )
                    )
    except Exception:
        # Graceful fallback if table finding fails on atypical vector drawings
        pass

    return extracted_tables
