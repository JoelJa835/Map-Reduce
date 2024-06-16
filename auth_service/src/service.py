from sqlalchemy.orm import Session
from models import User as UserModel
from schemas import User as UserSchema, UserCreate, UserRole
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

SECRET_KEY ="3db9c9e2e069d224d89837820888aacda3efb673a883ba5af71675e3726f9bdd"
EXPIRE_MINUTES = 60*24
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#check existing user with same username or email
async def check_existing_user(db: Session, username: str, email: str):
    db_user = db.query(UserModel).filter(UserModel.username == username).first() 
    if db_user:
        return db_user
    db_user = db.query(UserModel).filter(UserModel.email == email).first()
    if db_user:
        return db_user
    return None

#Create token
async def create_access_token(id: int, username: str):

    # Define the payload for the token
    payload = {
        "sub": username,
        "id": id,
    }
    # Set the expiration time for the token
    expiration = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    payload.update({"exp": expiration})

    # Generate the token using the secret key
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token

#get current user from token
async def get_current_user(db: Session, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        id: int = payload.get("id")
        expiration: datetime = payload.get("exp")
        if username is None or id is None:
            return None
        db_user = db.query(UserModel).filter(UserModel.id == id).first()
        return db_user
    except JWTError:
        return None


# Create user
async def create_user(db: Session, user: UserCreate, admin: bool = False):
    role = UserRole.admin if admin else user.role
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=bcrypt_context.hash(user.password),
        role=role
    )
    db.add(db_user)
    db.commit()
    return db_user

#authenticate user
async def authenticate_user(db: Session, username: str, password: str):
    db_user = db.query(UserModel).filter(UserModel.username == username).first()
    if db_user is None:
        return None
    if not bcrypt_context.verify(password, db_user.hashed_password):
        return None
    return db_user

# Check if the current user is an admin
async def is_admin(user: UserModel):
    return user.role == UserRole.admin
