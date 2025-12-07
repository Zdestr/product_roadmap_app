def tags_list_to_string(tags: list[str]) -> str | None:
    """
    Преобразует список тегов в нормализованную строку:
    - обрезает пробелы;
    - приводит к lower;
    - удаляет дубликаты;
    - сортирует.
    """
    if not tags:
        return None
    normalized = sorted(set(t.strip().lower() for t in tags if t.strip()))
    return ",".join(normalized) if normalized else None


def tags_string_to_list(tags_str: str | None) -> list[str]:
    """
    Преобразует строку тегов "tag1,tag2" обратно в список.
    """
    if not tags_str:
        return []
    return [t for t in tags_str.split(",") if t]
