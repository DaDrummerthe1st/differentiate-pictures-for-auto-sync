from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

# argon2id via argon2-cffi's PasswordHasher, OWASP's recommended algorithm
# for new applications over bcrypt/scrypt (resistant to GPU/ASIC cracking
# via its memory-hard design). Library defaults already sit within OWASP's
# recommended parameter range.
_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    try:
        _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
    return True


def needs_rehash(password_hash: str) -> bool:
    return _hasher.check_needs_rehash(password_hash)
