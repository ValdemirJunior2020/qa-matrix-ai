from app.security import hash_password, verify_password

def test_password_hash():
    h=hash_password("A-strong-test-password")
    assert "A-strong-test-password" not in h
    assert verify_password("A-strong-test-password",h)
    assert not verify_password("wrong-password",h)
