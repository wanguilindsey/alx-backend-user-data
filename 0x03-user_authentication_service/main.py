#!/usr/bin/env python3
"""Module for E2E integration tests for `app.py`.
"""

import requests
from app import AUTH

EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"
BASE_URL = "http://0.0.0.0:5000"


def register_user(email: str, password: str) -> None:
    """Test user registration."""
    url = f"{BASE_URL}/users"
    data = {"email": email, "password": password}
    response = requests.post(url, data=data)
    assert response.status_code == 200
    assert response.json() == {"email": email, "message": "user created"}
    response = requests.post(url, data=data)
    assert response.status_code == 400
    assert response.json() == {"message": "email already registered"}


def log_in_wrong_password(email: str, password: str) -> None:
    """Test login with incorrect password."""
    url = f"{BASE_URL}/sessions"
    data = {"email": email, "password": password}
    response = requests.post(url, data=data)
    assert response.status_code == 401


def profile_unlogged() -> None:
    """Test accessing profile without login."""
    url = f"{BASE_URL}/profile"
    response = requests.get(url)
    assert response.status_code == 403


def profile_logged(session_id: str) -> None:
    """Test retrieving profile while logged in."""
    url = f"{BASE_URL}/profile"
    cookies = {"session_id": session_id}
    response = requests.get(url, cookies=cookies)
    assert response.status_code == 200
    payload = response.json()
    assert "email" in payload
    user = AUTH.get_user_from_session_id(session_id)
    assert user.email == payload["email"]


def log_out(session_id: str) -> None:
    """Test logging out."""
    url = f"{BASE_URL}/sessions"
    headers = {"Content-Type": "application/json"}
    data = {"session_id": session_id}
    response = requests.delete(url, headers=headers, cookies=data)
    assert response.status_code == 200


def reset_password_token(email: str) -> str:
    """Test requesting a password reset token."""
    url = f"{BASE_URL}/reset_password"
    data = {"email": email}
    response = requests.post(url, data=data)
    assert response.status_code == 200
    assert response.json()["email"] == email
    return response.json()["reset_token"]


def update_password(email: str, reset_token: str, new_password: str) -> None:
    """Test updating the password."""
    url = f"{BASE_URL}/reset_password"
    data = {
        "email": email,
        "reset_token": reset_token,
        "new_password": new_password
    }
    response = requests.put(url, data=data)
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated"
    assert response.json()["email"] == email


def log_in(email: str, password: str) -> str:
    """Test login."""
    url = f"{BASE_URL}/sessions"
    data = {"email": email, "password": password}
    response = requests.post(url, data=data)
    if response.status_code == 401:
        return "Invalid credentials"
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["email"] == email
    return response.cookies.get("session_id")


if __name__ == "__main__":
    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
