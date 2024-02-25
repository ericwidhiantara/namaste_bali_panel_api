from fastapi import FastAPI, HTTPException, Form
from auth import AuthHandler
from models import UserModel

app = FastAPI()
auth_handler = AuthHandler()

@app.post("/register/")
async def register(email: str = Form(...), 
                                  first_name: str = Form(...), 
                                  last_name: str = Form(...), 
                                  username: str = Form(...), 
                                  password: str = Form(...), 
                                  password_confirmation: str = Form(...),):
    user = UserModel(email=email, first_name=first_name, last_name=last_name, username=username, password=password, password_confirmation=password_confirmation)
    res =  await auth_handler.register_user(user, password_confirmation)
    if not res: 
        raise HTTPException(status_code=400, detail="User already exists")
    return {"message": "User registered successfully"}

@app.post("/login/")
async def login(email: str = Form(...), password: str = Form(...)):
    user = await auth_handler.authenticate_user(email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    # Remove _id field if present
    user.pop("_id", None)
    user.pop("password", None)
    
    
    access_token = auth_handler.create_access_token({"sub": user["email"], "user":user})
    return {"access_token": access_token, "token_type": "bearer"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
