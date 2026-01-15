"""
File processing utilities for reading input files and generating output files.
"""

import os
from pathlib import Path
from typing import List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path to project root
    """
    # Assuming this file is in src/app/utils/
    return Path(__file__).parent.parent.parent.parent


def read_messages_from_file(file_path: str = "data/Sample Messages.txt") -> List[str]:
    """
    Read messages from a text file, one message per line.

    Args:
        file_path: Path to the messages file (can be absolute or relative to project root)

    Returns:
        List of messages (empty lines and whitespace stripped)

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    # Handle both absolute and relative paths
    path_obj = Path(file_path)
    if path_obj.is_absolute():
        full_path = path_obj
    else:
        root = get_project_root()
        full_path = root / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"Messages file not found: {full_path}")

    logger.info(f"Reading messages from: {full_path}")

    messages = []
    with open(full_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                messages.append(line)

    logger.info(f"Read {len(messages)} messages from file")
    return messages


def read_news_from_file(file_path: str = "data/News Feed.txt") -> List[str]:
    """
    Read news items from a text file, one item per line.

    Args:
        file_path: Path to the news feed file (can be absolute or relative to project root)

    Returns:
        List of news items (empty lines and whitespace stripped)

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    # Handle both absolute and relative paths
    path_obj = Path(file_path)
    if path_obj.is_absolute():
        full_path = path_obj
    else:
        root = get_project_root()
        full_path = root / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"News feed file not found: {full_path}")

    logger.info(f"Reading news items from: {full_path}")

    news_items = []
    with open(full_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                news_items.append(line)

    logger.info(f"Read {len(news_items)} news items from file")
    return news_items


def read_scenarios_from_file(file_path: str = "data/Scenarios.txt") -> List[str]:
    """
    Read crisis scenarios from a text file.
    Scenarios are separated by blank lines.

    Args:
        file_path: Path to the scenarios file (relative to project root)

    Returns:
        List of scenarios (each scenario is a multi-line string)

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    root = get_project_root()
    full_path = root / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"Scenarios file not found: {full_path}")

    logger.info(f"Reading scenarios from: {full_path}")

    scenarios = []
    current_scenario = []

    with open(full_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # Non-empty line
                current_scenario.append(line)
            else:  # Empty line - scenario separator
                if current_scenario:
                    scenarios.append('\n'.join(current_scenario))
                    current_scenario = []

        # Add last scenario if exists
        if current_scenario:
            scenarios.append('\n'.join(current_scenario))

    logger.info(f"Read {len(scenarios)} scenarios from file")
    return scenarios


def read_incidents_from_file(file_path: str = "data/Incidents.txt") -> List[str]:
    """
    Read incident descriptions from a text file, one incident per line.

    Args:
        file_path: Path to the incidents file (relative to project root)

    Returns:
        List of incident descriptions (empty lines and whitespace stripped)

    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    root = get_project_root()
    full_path = root / file_path

    if not full_path.exists():
        raise FileNotFoundError(f"Incidents file not found: {full_path}")

    logger.info(f"Reading incidents from: {full_path}")

    incidents = []
    with open(full_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                incidents.append(line)

    logger.info(f"Read {len(incidents)} incidents from file")
    return incidents


def ensure_output_directory() -> Path:
    """
    Ensure the output directory exists.
    
    Returns:
        Path to output directory
    """
    root = get_project_root()
    output_dir = root / "output"
    output_dir.mkdir(exist_ok=True)
    logger.info(f"Output directory ready: {output_dir}")
    return output_dir


def save_classification_results_to_csv(results: List[dict], filename: str = "classified_messages.csv") -> str:
    """
    Save classification results to CSV file.
    
    Args:
        results: List of classification result dictionaries
        filename: Output filename
    
    Returns:
        Absolute path to the saved CSV file
    """
    output_dir = ensure_output_directory()
    file_path = output_dir / filename
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Reorder columns for better readability
    column_order = ['message', 'district', 'intent', 'priority', 'raw_output']
    existing_columns = [col for col in column_order if col in df.columns]
    df = df[existing_columns]
    
    # Save to CSV
    df.to_csv(file_path, index=False, encoding='utf-8')
    logger.info(f"Saved {len(results)} classification results to CSV: {file_path}")
    
    return str(file_path)


def save_classification_results_to_excel(results: List[dict], filename: str = "classified_messages.xlsx") -> str:
    """
    Save classification results to Excel file with formatting.
    
    Args:
        results: List of classification result dictionaries
        filename: Output filename
    
    Returns:
        Absolute path to the saved Excel file
    """
    output_dir = ensure_output_directory()
    file_path = output_dir / filename
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Reorder columns for better readability
    column_order = ['message', 'district', 'intent', 'priority', 'raw_output']
    existing_columns = [col for col in column_order if col in df.columns]
    df = df[existing_columns]
    
    # Save to Excel with formatting
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Classifications')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Classifications']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            )
            # Cap at 50 characters for readability
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
    
    logger.info(f"Saved {len(results)} classification results to Excel: {file_path}")
    
    return str(file_path)


def save_crisis_events_to_excel(events: List[dict], filename: str = "flood_report.xlsx") -> str:
    """
    Save crisis events to Excel file with formatting.
    
    Args:
        events: List of crisis event dictionaries
        filename: Output filename
    
    Returns:
        Absolute path to the saved Excel file
    """
    output_dir = ensure_output_directory()
    file_path = output_dir / filename
    
    # Convert to DataFrame
    df = pd.DataFrame(events)

    # Reorder columns for better readability
    # Support both old (flood_level_m) and new (flood_level_meters) field names
    column_order = ['district', 'flood_level_meters', 'victim_count', 'main_need', 'status']
    # Fallback to old name if new name doesn't exist
    if 'flood_level_meters' not in df.columns and 'flood_level_m' in df.columns:
        column_order = ['district', 'flood_level_m', 'victim_count', 'main_need', 'status']

    existing_columns = [col for col in column_order if col in df.columns]
    df = df[existing_columns]

    # Rename columns for better presentation
    rename_map = {
        'flood_level_meters': 'Flood Level (m)',
        'flood_level_m': 'Flood Level (m)',
        'victim_count': 'Victim Count',
        'district': 'District',
        'main_need': 'Main Need',
        'status': 'Status'
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})
    
    # Save to Excel with formatting
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Crisis Events')
        
        # Auto-adjust column widths
        worksheet = writer.sheets['Crisis Events']
        for idx, col in enumerate(df.columns):
            max_length = max(
                df[col].astype(str).apply(len).max(),
                len(col)
            )
            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 30)
    
    logger.info(f"Saved {len(events)} crisis events to Excel: {file_path}")
    
    return str(file_path)

