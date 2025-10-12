from uuid import UUID
import string
import random
from passlib.context import CryptContext
import bcrypt


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password:str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)
    return hashed_password.decode()

def verify_password(hashed_password:str, plain_password:str) -> bool:
    password:bytes = plain_password.encode()
    if bcrypt.checkpw(password, hashed_password.encode()):
        return True
    return False

def generate_password(tenant_uuid: UUID, user_uuid: UUID) -> str:
    # Combine both UUIDs to form a reproducible seed
    seed_value = str(tenant_uuid) + str(user_uuid)
    random.seed(seed_value)  # ensures same inputs -> same output

    # Required characters
    uppercase = random.choice(string.ascii_uppercase)
    digit = random.choice(string.digits)
    special = random.choice("!@#$%^&*()-_=+")

    # Choose a random total length between 5 and 10
    password_length = random.randint(5, 10)

    # Pool for remaining characters
    all_chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    remaining_length = password_length - 3  # already added 3 required chars

    remaining_chars = [random.choice(all_chars) for _ in range(remaining_length)]

    # Combine all and shuffle
    password_chars = list(uppercase + digit + special) + remaining_chars
    random.shuffle(password_chars)
    return hash_password("".join(password_chars))

