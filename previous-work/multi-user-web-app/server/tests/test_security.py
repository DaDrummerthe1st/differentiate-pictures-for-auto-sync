from argon2 import PasswordHasher
from argon2.low_level import Type

from app.security import hash_password, needs_rehash, verify_password


def test_hash_and_verify_round_trip():
    password_hash = hash_password("correct horse battery staple")

    assert verify_password("correct horse battery staple", password_hash) is True


def test_verify_rejects_wrong_password():
    password_hash = hash_password("correct horse battery staple")

    assert verify_password("wrong password", password_hash) is False


def test_hash_uses_argon2id_variant():
    password_hash = hash_password("correct horse battery staple")

    assert password_hash.startswith("$argon2id$")


def test_needs_rehash_is_false_for_a_freshly_produced_hash():
    password_hash = hash_password("correct horse battery staple")

    assert needs_rehash(password_hash) is False


def test_needs_rehash_is_true_for_a_weaker_hash():
    weak_hasher = PasswordHasher(time_cost=1, memory_cost=8, parallelism=1, type=Type.ID)
    weak_hash = weak_hasher.hash("correct horse battery staple")

    assert needs_rehash(weak_hash) is True
