from re import template
from fastapi import FastAPI, Request, HTTPException, status
from tortoise import models
from tortoise.contrib.fastapi import register_tortoise
from models import *
from authentication import (get_hashed_password, very_token)

# signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from emails import *

# response classes
from fastapi.responses import HTMLResponse

# tempalte 
from fastapi.responses import Jinja2Tamplate




app = FastAPI()

@post_save(User)
async def create_business(
    sender: "Type[User]",
    instance: User,
    create: bool,
    using_db: "Optional[BaseDBAsyncClient]",
    update_fiels:List[str]
) -> None:
    
    if create:
        business_obj = await Business.create(
            business_name = instance.username, owner = instance
        )
        await business_pydentic.from_tortoise_orm(business_obj)
        # send Email
        await send_email([instance.email], instance)

@app.post("/registration")
async def user_registrations(user: user_pydantic):
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = get_hashed_password(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    return {
        "status": "ok",
        "data" : f"hello {new_user.username}, thanks for choosing our services. Please check your email inbox and click the link to confirm your registration"
    }
tempaltes = Jinja2Tamplate(directory="templates")  

@app.get('/verification', response_class=HTMLResponse)
async def email_verification(request: Request, token: str):
    user = await very_token(token)
    
    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return tempaltes.TemplateResponce("verification.html", 
                                          {"request" : request, "username": user.
                                            username})
        
    raise HTTPException (
         status_code= status.HTTP_401_UNAUTHORIZED,
         detail = "Invalid token or expired token",
         headers= {"WWW.Authenticates": "Bearer"} 
       )    


      

@app.get('/')
def index():
    return{"Message": "Hello World"}


register_tortoise(
    app,
    db_url="sqlite://database.dqlite3",
    modules= {"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)