from dataclasses import dataclass, field


@dataclass
class Contact:
    """Provider-agnostic contact record — every importer normalizes into this shape."""

    display_name: str
    emails: list[str] = field(default_factory=list)
    source: str = ""
