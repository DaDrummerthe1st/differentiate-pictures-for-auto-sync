import vobject

from contacts.models import Contact


def _flatten(value):
    # vobject represents structured properties (ORG, N, ADR, ...) as a list
    # of components even when there's only one - collapse that single-item
    # case to a plain string so `raw` reads like a normal flat record.
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value


def _raw_properties(card) -> dict:
    raw = {}
    for lines in card.contents.values():
        name = lines[0].name
        raw[name] = _flatten(lines[0].value) if len(lines) == 1 else [_flatten(l.value) for l in lines]
    return raw


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
        contacts.append(
            Contact(display_name=display_name, emails=emails, source="vcard", raw=_raw_properties(card))
        )
    return contacts
