from dataclasses import dataclass

from contacts.models import Contact


@dataclass
class RenameEvent:
    old_name: str
    new_name: str
    email: str


def detect_renames(before: list[Contact], after: list[Contact]) -> list[RenameEvent]:
    """Detect a contact's display name changing between two snapshots.

    Matches by email, never by name — email is the closest thing to a stable
    identifier a CSV export gives us (no true resourceName/UID like the People
    API or a vCard's UID field), so a name change is only ever inferred from the
    *same* email now carrying a *different* name, never assumed from the name
    itself. A contact with no email can never be matched this way — there is
    nothing stable to key on for it.
    """
    before_by_email = {email: c.display_name for c in before for email in c.emails}
    renames = []
    for contact in after:
        for email in contact.emails:
            old_name = before_by_email.get(email)
            if old_name is not None and old_name != contact.display_name:
                renames.append(RenameEvent(old_name=old_name, new_name=contact.display_name, email=email))
    return renames
