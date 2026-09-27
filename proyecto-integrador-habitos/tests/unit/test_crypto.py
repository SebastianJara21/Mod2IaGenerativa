"""Tests for cryptographic password hashing and verification utilities."""

import pytest
from app.utils.crypto import hash_password, verify_password


def test_hash_password_produces_bcrypt_hash():
    """Verify hash_password produces a bcrypt-format hash."""
    password = "test_password_123"
    hashed = hash_password(password)

    # Bcrypt hashes start with $2a$, $2b$, or $2y$ and are ~60 chars
    assert hashed.startswith(("$2a$", "$2b$", "$2y$"))
    assert len(hashed) >= 60
    # Hash should not equal plaintext
    assert hashed != password


def test_hash_password_different_salts():
    """Verify same password hashes differently (due to random salt)."""
    password = "test_password_123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Hashes should be different due to random salt
    assert hash1 != hash2


def test_verify_password_correct_password():
    """Verify verify_password returns True for correct password."""
    password = "my_secure_password"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect_password():
    """Verify verify_password returns False for incorrect password."""
    password = "correct_password"
    wrong_password = "wrong_password"
    hashed = hash_password(password)

    assert verify_password(wrong_password, hashed) is False


def test_verify_password_empty_string():
    """Verify verify_password handles empty string correctly."""
    hashed = hash_password("nonempty_password")

    # Empty string should not verify
    assert verify_password("", hashed) is False


def test_hash_and_verify_roundtrip():
    """Verify hash and verify work together in a roundtrip."""
    original_password = "complex_P@ssw0rd_123"

    # Hash the password
    hashed = hash_password(original_password)

    # Verify it matches
    assert verify_password(original_password, hashed) is True

    # Verify a typo does not match
    assert verify_password("complex_P@ssw0rd_124", hashed) is False
