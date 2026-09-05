import pytest

from contacts.multipart import extract_uploaded_file

# Synthetic fixture bytes only, same convention as the rest of contacts/tests.


def _multipart_body(field_name: str, filename: str, content: bytes, boundary: str = "BOUNDARY123") -> bytes:
    return (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'
        f"Content-Type: text/csv\r\n\r\n"
    ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")


def test_extracts_file_content_and_filename():
    body = _multipart_body("csv_file", "export.csv", b"First Name,Last Name\nAlice,Andersson\n")
    content_type = "multipart/form-data; boundary=BOUNDARY123"

    filename, content = extract_uploaded_file(content_type, body)

    assert filename == "export.csv"
    assert content == b"First Name,Last Name\nAlice,Andersson\n"


def test_ignores_non_file_fields_and_finds_the_file_among_them():
    boundary = "BOUNDARY123"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="mode"\r\n\r\n'
        f"upload\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="csv_file"; filename="real.csv"\r\n'
        f"Content-Type: text/csv\r\n\r\n"
        f"a,b\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")
    content_type = f"multipart/form-data; boundary={boundary}"

    filename, content = extract_uploaded_file(content_type, body)

    assert filename == "real.csv"
    assert content == b"a,b"


def test_raises_when_content_type_is_not_multipart():
    with pytest.raises(ValueError):
        extract_uploaded_file("application/x-www-form-urlencoded", b"a=b")


def test_raises_when_no_file_field_present():
    boundary = "BOUNDARY123"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="mode"\r\n\r\n'
        f"upload\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")
    with pytest.raises(ValueError):
        extract_uploaded_file(f"multipart/form-data; boundary={boundary}", body)
