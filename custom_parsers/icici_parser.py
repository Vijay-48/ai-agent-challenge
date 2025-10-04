import pdfplumber
import pandas as pd
import re

def parse(pdf_path: str) -> pd.DataFrame:
    all_transactions_data = []
    expected_headers = ['Date', 'Description', 'Debit Amt', 'Credit Amt', 'Balance']

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue

                for row in table:
                    # Clean and standardize row cells: strip spaces, handle None
                    # If a cell is None, treat it as an empty string. Otherwise, convert to string and strip.
                    cleaned_row = [
                        cell.strip() if isinstance(cell, str) else '' if cell is None else str(cell).strip()
                        for cell in row
                    ]

                    # Filter out rows that are clearly not transaction data or are malformed
                    # A valid transaction row must have at least 5 columns and start with a date.
                    if len(cleaned_row) < len(expected_headers):
                        continue

                    # Check if the first element matches the DD-MM-YYYY date pattern
                    # This is the primary heuristic for identifying a transaction data row.
                    if re.match(r'^\d{2}-\d{2}-\d{4}$', cleaned_row[0]):
                        # This is identified as a data row
                        # Ensure we only take the first `len(expected_headers)` elements
                        # to match the schema and truncate any extra columns.
                        all_transactions_data.append(cleaned_row[:len(expected_headers)])
                    else:
                        # This could be a header row or some other non-transaction text.
                        # We explicitly check for and skip header rows to prevent them from being processed as data.
                        
                        # Normalize header strings for robust comparison (e.g., handle extra spaces, case-insensitivity)
                        normalized_row_for_header_check = [
                            re.sub(r'\s+', ' ', h.strip()).lower() if h else ''
                            for h in cleaned_row[:len(expected_headers)]
                        ]
                        normalized_expected_headers = [
                            re.sub(r'\s+', ' ', h.strip()).lower()
                            for h in expected_headers
                        ]
                        
                        if normalized_row_for_header_check == normalized_expected_headers:
                            # This is a header row, skip it.
                            pass
                        else:
                            # It's neither a recognizable data row nor a header row, so ignore it.
                            pass

    # Create DataFrame from collected data
    df = pd.DataFrame(all_transactions_data, columns=expected_headers)

    # Type conversion and missing value handling
    # Date: Keep as string (DD-MM-YYYY format) as per sample output.
    # Description: String (already handled during row cleaning).

    # Debit Amt, Credit Amt, Balance: Convert to float.
    # Handle potential thousands separators (commas) and empty strings.
    # Empty strings in these columns should become NaN in the float DataFrame columns as per sample output.
    for col in ['Debit Amt', 'Credit Amt', 'Balance']:
        # Replace commas (e.g., "1,000.00") if present, though not in sample.
        df[col] = df[col].str.replace(',', '', regex=False)
        
        # Replace empty strings with pd.NA (Pandas' nullable missing value indicator).
        # This is important for correct conversion to NaN in float columns.
        df[col] = df[col].replace('', pd.NA)
        
        # Convert the column to numeric (float).
        # `errors='coerce'` will turn any values that cannot be converted to a number into NaN.
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    return df