from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models import User as UserModel
from schemas import User as UserSchema, UserCreate
from database import get_db,engine
from sqlalchemy.orm import Session
import service
import models

app = FastAPI()


models.Base.metadata.create_all(bind=engine)


@app.post("/initial-admin", status_code=status.HTTP_201_CREATED)
async def create_initial_admin(user: UserCreate, db: Session = Depends(get_db)):
    # Check if there are any users in the database
    if db.query(UserModel).first():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Initial admin already created")

    # Create the initial admin user
    db_user = await service.create_user(db, user, admin=True)
    access_token = await service.create_access_token(db_user.id, db_user.username)
    return {"access_token": access_token, "token_type": "bearer", "username": db_user.username}


# @app.post("/signup", status_code=status.HTTP_201_CREATED)
# async def create_user(user: UserCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(service.get_current_user)):

#     if not current_user or not await service.is_admin(current_user):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
#     db_user = await service.check_existing_user(db, user.username, user.email)
#     print(db_user)
#     if db_user:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username  already exists")
#     db_user = await service.create_user(db, user)
#     access_token = await service.create_access_token(db_user.id, db_user.username)

#     return {"access_token": access_token, "token_type": "bearer", "username": db_user.username}

@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate, 
    db: Session = Depends(get_db), 
    token: str = Depends(service.oauth2_scheme)
):
    current_user = await service.get_current_user(db, token)
    if not current_user or not await service.is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    db_user = await service.check_existing_user(db, user.username, user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists")

    db_user = await service.create_user(db, user)
    access_token = await service.create_access_token(db_user.id, db_user.username)
    return {"access_token": access_token, "token_type": "bearer", "username": db_user.username}


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = await service.authenticate_user(db, form_data.username, form_data.password)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = await service.create_access_token(db_user.id, db_user.username)
    return {"access_token": access_token, "token_type": "bearer"}


# @app.post("/create-admin", status_code=status.HTTP_201_CREATED)
# async def create_admin(user: UserCreate, db: Session = Depends(get_db), current_user: UserModel = Depends(service.get_current_user)):
#     if not current_user or not await service.is_admin(current_user):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
#     db_user = await service.check_existing_user(db, user.username, user.email)
#     if db_user:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists")
#     db_user = await service.create_user(db, user, admin=True)
#     access_token = await service.create_access_token(db_user.id, db_user.username)
#     return {"access_token": access_token, "token_type": "bearer", "username": db_user.username}


# @app.post("/create-admin", status_code=status.HTTP_201_CREATED)
# async def create_admin(
#     user: UserCreate, 
#     db: Session = Depends(get_db), 
#     token: str = Depends(service.oauth2_scheme)
# ):
#     current_user = await service.get_current_user(db, token)
#     if not current_user or not await service.is_admin(current_user):
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

#     db_user = await service.check_existing_user(db, user.username, user.email)
#     if db_user:
#         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username or email already exists")

#     db_user = await service.create_user(db, user, admin=True)
#     access_token = await service.create_access_token(db_user.id, db_user.username)
#     return {"access_token": access_token, "token_type": "bearer", "username": db_user.username}