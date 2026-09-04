from contacts.matching import detect_renames
from contacts.models import Contact


def test_no_renames_when_nothing_changed():
    before = [Contact(display_name="Alice Andersson", emails=["alice@example.com"])]
    after = [Contact(display_name="Alice Andersson", emails=["alice@example.com"])]
    assert detect_renames(before, after) == []


def test_detects_a_rename_by_matching_email():
    before = [Contact(display_name="Per Holmgren", emails=["per@example.com"])]
    after = [Contact(display_name="Per H.", emails=["per@example.com"])]
    renames = detect_renames(before, after)
    assert len(renames) == 1
    assert renames[0].old_name == "Per Holmgren"
    assert renames[0].new_name == "Per H."
    assert renames[0].email == "per@example.com"


def test_a_shared_email_between_two_different_people_is_not_a_rename():
    # Different name, no email overlap at all — a brand new contact, not a rename.
    before = [Contact(display_name="Alice Andersson", emails=["alice@example.com"])]
    after = [
        Contact(display_name="Alice Andersson", emails=["alice@example.com"]),
        Contact(display_name="Bo Bengtsson", emails=["bo@example.com"]),
    ]
    assert detect_renames(before, after) == []


def test_a_contact_with_no_email_can_never_be_matched_for_rename():
    before = [Contact(display_name="No Email Nilsson", emails=[])]
    after = [Contact(display_name="Renamed Nilsson", emails=[])]
    assert detect_renames(before, after) == []
