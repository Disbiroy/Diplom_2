import random
import string

def generate_random_email():
    username = ''.join(random.choices(string.ascii_lowercase, k=8))
    return f"{username}@test.com"

def generate_random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def generate_random_name():
    return ''.join(random.choices(string.ascii_letters, k=8))

# Тестовые данные
VALID_USER = {
    "email": generate_random_email(),
    "password": generate_random_password(),
    "name": generate_random_name()
}

EXISTING_USER = {
    "email": "existing_user@test.com",
    "password": "password123",
    "name": "Existing User"
}

INVALID_USER_MISSING_EMAIL = {
    "email": None,
    "password": "password123",
    "name": "Test User"
}

INVALID_USER_MISSING_PASSWORD = {
    "email": generate_random_email(),
    "password": None,
    "name": "Test User"
}