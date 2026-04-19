def bulletize(items: List[str]) -> str:
    return "\n".join(f"- {item}" for item in items)
