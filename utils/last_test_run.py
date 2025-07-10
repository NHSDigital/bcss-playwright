import os
import json
from datetime import date
from typing import Dict, Any, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LAST_RUN_FILE = os.path.join(PROJECT_ROOT, ".test_last_runs.json")


def load_last_run_data() -> Dict[str, Any]:
    """
    Loads the last run data from the JSON file.

    Returns:
        Dict[str, Any]: A dictionary mapping test names to their last run date.
    """
    if os.path.exists(LAST_RUN_FILE):
        try:
            with open(LAST_RUN_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_last_run_data(data: Dict[str, Any]) -> None:
    """
    Saves the last run data to the JSON file.

    Args:
        data (Dict[str, Any]): The data to save, mapping test names to their last run date.
    """
    with open(LAST_RUN_FILE, "w") as f:
        json.dump(data, f, indent=2)


def has_test_run_today(test_name: str, base_url: Optional[str] = None) -> bool:
    """
    Checks if the given test has already run today.
    If not, updates the record to mark it as run today.

    Args:
        test_name (str): The name of the test to check.

    Returns:
        bool: True if the test has already run today, False otherwise.
    """
    data = load_last_run_data()
    today = date.today().isoformat()
    env = base_url or "unknown"

    last_run = data.get(test_name, {})
    if last_run.get("date") == today and last_run.get("env") == env:
        return True
    else:
        data[test_name] = {"date": today, "env": env}
        save_last_run_data(data)
        return False
