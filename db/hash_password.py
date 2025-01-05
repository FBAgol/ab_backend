from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hash: 
    # Hashing the password
    def bcrypt(self, password: str):
        return pwd_context.hash(password)

    # Verifying the password
    def verify(self, hashed_password, plain_password):
        return pwd_context.verify(plain_password, hashed_password)
    