from dataclasses import dataclass, field


@dataclass
class Contact:
    """Provider-agnostic contact record — every importer normalizes into this shape."""

    display_name: str
    emails: list[str] = field(default_factory=list)
    source: str = ""
    # The full original source row/record (every CSV column, every vCard
    # property) beyond the few promoted to first-class fields above — needed
    # so dedup/merge in contacts/db.py can compare whole records, not just
    # display_name and emails.
    raw: dict = field(default_factory=dict)
