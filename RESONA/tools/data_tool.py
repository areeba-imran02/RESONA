"""
RESONA - Data Processing Tool

Handles CSV and Excel emergency-response datasets.

Supported formats:
- CSV
- XLSX
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


SUPPORTED_DATA_EXTENSIONS = {
    ".csv",
    ".xlsx",
}


class DataProcessingError(Exception):
    """Raised when a dataset cannot be processed."""


def _validate_data_file(
    file_path: str,
) -> Path:
    """Validate a CSV or Excel file path."""

    if not file_path or not file_path.strip():
        raise DataProcessingError(
            "Data file path cannot be empty."
        )

    path = Path(file_path)

    if not path.exists():
        raise DataProcessingError(
            f"Data file not found: {file_path}"
        )

    if not path.is_file():
        raise DataProcessingError(
            f"Provided path is not a file: {file_path}"
        )

    if path.suffix.lower() not in SUPPORTED_DATA_EXTENSIONS:
        raise DataProcessingError(
            "Unsupported data format. "
            "Supported formats: CSV and XLSX."
        )

    return path


def read_csv_file(
    file_path: str,
) -> pd.DataFrame:
    """
    Read a CSV file into a pandas DataFrame.
    """

    path = _validate_data_file(file_path)

    if path.suffix.lower() != ".csv":
        raise DataProcessingError(
            "read_csv_file only accepts CSV files."
        )

    try:
        return pd.read_csv(path)

    except Exception as exc:
        raise DataProcessingError(
            f"Unable to read CSV file: {exc}"
        ) from exc


def read_excel_file(
    file_path: str,
    sheet_name: Optional[str] = None,
) -> pd.DataFrame:
    """
    Read an Excel workbook.

    If sheet_name is not provided, the first sheet is used.
    """

    path = _validate_data_file(file_path)

    if path.suffix.lower() != ".xlsx":
        raise DataProcessingError(
            "read_excel_file only accepts XLSX files."
        )

    try:
        if sheet_name:
            return pd.read_excel(
                path,
                sheet_name=sheet_name,
            )

        return pd.read_excel(
            path
        )

    except Exception as exc:
        raise DataProcessingError(
            f"Unable to read Excel file: {exc}"
        ) from exc


def read_dataset(
    file_path: str,
    sheet_name: Optional[str] = None,
) -> pd.DataFrame:
    """
    Read a supported dataset based on its extension.
    """

    path = _validate_data_file(file_path)

    if path.suffix.lower() == ".csv":
        return read_csv_file(
            str(path)
        )

    if path.suffix.lower() == ".xlsx":
        return read_excel_file(
            str(path),
            sheet_name=sheet_name,
        )

    raise DataProcessingError(
        "Unsupported dataset format."
    )


def clean_dataset(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Perform conservative data cleaning.

    The function:
    - removes completely empty rows
    - removes completely empty columns
    - trims whitespace from column names
    - trims whitespace from string values
    """

    if dataframe is None:
        raise DataProcessingError(
            "Dataset cannot be None."
        )

    if not isinstance(
        dataframe,
        pd.DataFrame,
    ):
        raise DataProcessingError(
            "Input must be a pandas DataFrame."
        )

    cleaned = dataframe.copy()

    # Remove fully empty rows and columns.
    cleaned = cleaned.dropna(
        how="all"
    )

    cleaned = cleaned.dropna(
        axis=1,
        how="all",
    )

    # Normalize column names.
    cleaned.columns = [
        str(column).strip()
        for column in cleaned.columns
    ]

    # Trim string values without changing
    # numeric or datetime columns.
    for column in cleaned.columns:

        if pd.api.types.is_object_dtype(
            cleaned[column]
        ):
            cleaned[column] = (
                cleaned[column]
                .astype("string")
                .str.strip()
            )

    return cleaned.reset_index(
        drop=True
    )


def validate_dataset(
    dataframe: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Return basic structural validation information.
    """

    if not isinstance(
        dataframe,
        pd.DataFrame,
    ):
        raise DataProcessingError(
            "Input must be a pandas DataFrame."
        )

    columns = [
        str(column)
        for column in dataframe.columns
    ]

    missing_values = {}

    for column in dataframe.columns:

        missing_count = int(
            dataframe[column]
            .isna()
            .sum()
        )

        if missing_count > 0:
            missing_values[
                str(column)
            ] = missing_count

    duplicate_rows = int(
        dataframe.duplicated().sum()
    )

    return {
        "valid": not dataframe.empty,
        "row_count": int(
            len(dataframe)
        ),
        "column_count": int(
            len(dataframe.columns)
        ),
        "columns": columns,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "empty_dataset": bool(
            dataframe.empty
        ),
    }


def summarize_dataset(
    dataframe: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Generate a compact statistical summary.

    Numeric columns receive:
    - count
    - mean
    - minimum
    - maximum

    Categorical columns receive:
    - unique count
    - most common value
    """

    if not isinstance(
        dataframe,
        pd.DataFrame,
    ):
        raise DataProcessingError(
            "Input must be a pandas DataFrame."
        )

    if dataframe.empty:
        return {
            "row_count": 0,
            "column_count": 0,
            "numeric_columns": {},
            "categorical_columns": {},
        }

    numeric_summary = {}
    categorical_summary = {}

    for column in dataframe.columns:

        series = dataframe[column]

        if pd.api.types.is_numeric_dtype(
            series
        ):

            numeric_series = series.dropna()

            if numeric_series.empty:
                continue

            numeric_summary[
                str(column)
            ] = {
                "count": int(
                    numeric_series.count()
                ),
                "mean": round(
                    float(
                        numeric_series.mean()
                    ),
                    2,
                ),
                "minimum": float(
                    numeric_series.min()
                ),
                "maximum": float(
                    numeric_series.max()
                ),
            }

        else:

            non_null = series.dropna()

            if non_null.empty:
                continue

            value_counts = (
                non_null
                .astype(str)
                .value_counts()
            )

            top_value = (
                str(value_counts.index[0])
                if not value_counts.empty
                else None
            )

            top_count = (
                int(value_counts.iloc[0])
                if not value_counts.empty
                else 0
            )

            categorical_summary[
                str(column)
            ] = {
                "unique_values": int(
                    non_null.nunique()
                ),
                "most_common": top_value,
                "most_common_count": top_count,
            }

    return {
        "row_count": int(
            len(dataframe)
        ),
        "column_count": int(
            len(dataframe.columns)
        ),
        "numeric_columns": numeric_summary,
        "categorical_columns": categorical_summary,
    }


def dataframe_to_records(
    dataframe: pd.DataFrame,
    max_rows: int = 500,
) -> List[Dict[str, Any]]:
    """
    Convert a DataFrame into JSON-friendly records.

    A row limit prevents accidentally sending an extremely
    large dataset directly into an LLM context.
    """

    if not isinstance(
        dataframe,
        pd.DataFrame,
    ):
        raise DataProcessingError(
            "Input must be a pandas DataFrame."
        )

    max_rows = max(
        int(max_rows),
        1,
    )

    limited = dataframe.head(
        max_rows
    ).copy()

    # Replace NaN/NaT with None.
    limited = limited.where(
        pd.notnull(limited),
        None,
    )

    records = limited.to_dict(
        orient="records"
    )

    # Make values JSON-friendly.
    cleaned_records = []

    for record in records:

        cleaned_record = {}

        for key, value in record.items():

            if hasattr(
                value,
                "isoformat",
            ):
                value = value.isoformat()

            elif hasattr(
                value,
                "item",
            ):
                try:
                    value = value.item()
                except Exception:
                    pass

            cleaned_record[
                str(key)
            ] = value

        cleaned_records.append(
            cleaned_record
        )

    return cleaned_records


def build_dataset_context(
    dataframe: pd.DataFrame,
    max_rows: int = 100,
) -> Dict[str, Any]:
    """
    Build a structured context package for the agent workflow.

    It contains:
    - validation information
    - statistical summary
    - sample records
    """

    cleaned = clean_dataset(
        dataframe
    )

    return {
        "validation": validate_dataset(
            cleaned
        ),
        "summary": summarize_dataset(
            cleaned
        ),
        "sample_records": dataframe_to_records(
            cleaned,
            max_rows=max_rows,
        ),
    }


def get_data_tools() -> Dict[str, callable]:
    """
    Return data-processing functions in a simple registry.
    """

    return {
        "read_dataset": read_dataset,
        "clean_dataset": clean_dataset,
        "validate_dataset": validate_dataset,
        "summarize_dataset": summarize_dataset,
        "dataframe_to_records": dataframe_to_records,
        "build_dataset_context": build_dataset_context,
    }
