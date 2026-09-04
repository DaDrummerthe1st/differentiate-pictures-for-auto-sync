import vobject

from contacts.models import Contact


def parse_vcard(vcard_text: str) -> list[Contact]:
    """Parse one or more vCards (RFC 6350) into normalized Contact records.

    vCard is the one interchange format every major contacts provider (Google,
    iCloud, Outlook, Apple Contacts) can export, and what CardDAV itself returns
    under the hood — this is the genuinely provider-agnostic importer, not a
    per-vendor guess.
    """
    contacts = []
    for card in vobject.readComponents(vcard_text):
        display_name = card.fn.value
        emails = [email.value for email in getattr(card, "email_list", [])]
        contacts.append(Contact(display_name=display_name, emails=emails, source="vcard"))
    return contacts
