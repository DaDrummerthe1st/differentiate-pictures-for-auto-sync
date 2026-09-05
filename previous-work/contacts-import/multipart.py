"""Minimal multipart/form-data parsing for the one thing contacts/web/server.py
needs: pulling a single uploaded file's bytes and filename out of a plain
HTML <form method=post enctype=multipart/form-data> submission.

Python removed the `cgi` module (which used to do this) in 3.13. Rather than
add a dependency for one small parse, this treats the body as what it
actually is - a MIME multipart message - and hands it to the stdlib's
`email` parser, which already understands that format.
"""
from email import message_from_bytes
from email.policy import compat32


def extract_uploaded_file(content_type: str, body: bytes) -> tuple[str, bytes]:
    """Returns (filename, content) for the first file field found.

    Raises ValueError if content_type isn't multipart/form-data, or no part
    has a filename (i.e. no file was actually chosen/uploaded).
    """
    if not content_type.startswith("multipart/form-data"):
        raise ValueError(f"Expected multipart/form-data, got: {content_type}")

    # email.message_from_bytes needs MIME headers above the body to know the
    # boundary; a raw HTTP multipart body only carries them via the request's
    # Content-Type header, so reattach that header before parsing.
    message = message_from_bytes(f"Content-Type: {content_type}\r\n\r\n".encode("ascii") + body, policy=compat32)

    for part in message.walk():
        filename = part.get_filename()
        if filename:
            return filename, part.get_payload(decode=True)

    raise ValueError("No file field found in multipart/form-data body")
