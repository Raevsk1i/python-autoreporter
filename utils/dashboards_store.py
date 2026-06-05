"""Загрузка и сохранение дашбордов из dashboards.json."""

import json
from pathlib import Path
from typing import Any


def load_dashboards_data(path: str | Path) -> dict[str, Any]:
    """
    Загружает словарь дашбордов из JSON-файла.

    Args:
        path: Путь к dashboards.json.

    Returns:
        Словарь дашбордов в формате JSON.
    """
    dashboards_path = Path(path)

    if not dashboards_path.is_file():
        return {}

    with open(dashboards_path, encoding="utf-8") as file:
        return json.load(file)


def save_dashboards_data(path: str | Path, data: dict[str, Any]) -> None:
    """
    Сохраняет словарь дашбордов в JSON-файл.

    Args:
        path: Путь к dashboards.json.
        data: Словарь дашбордов для записи.
    """
    dashboards_path = Path(path)
    dashboards_path.parent.mkdir(parents=True, exist_ok=True)

    with open(dashboards_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
