def sanitize_filename(name):
    safe_chars = []
    for char in name:
        if char.isalnum() or char in {"-", "_", "."}:
            safe_chars.append(char)
        else:
            safe_chars.append("_")
    cleaned = "".join(safe_chars).strip("._")
    return cleaned or "audio"


def format_seconds(value):
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    if "." not in text:
        text += ".0"
    return text


def format_milliseconds(value):
    if value >= 1000:
        return f"{value / 1000:.2f}s"
    return f"{value:.1f}ms"
