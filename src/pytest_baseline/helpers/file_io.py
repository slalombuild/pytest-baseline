import csv
from pathlib import Path
from typing import Any, Dict, List, Optional


def generate_csv_file(
    file_name: str,
    file_directory: Path,
    data: List[Dict[str, Any]],
    delimiter: Optional[str] = None
) -> str:
    """Generates a csv file with the passed data, returns the created file's
    path
    """
    file_path = file_directory / file_name

    # Determine headers
    headers = set()
    for item in data:
        headers.update(item.keys())

    # Open file and write the lines
    with open(file_path, "w") as f:
        dict_writer = csv.DictWriter(f, headers, delimiter=delimiter)
        dict_writer.writeheader()
        dict_writer.writerows(data)

    return file_path
