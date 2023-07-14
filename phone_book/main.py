from fastapi import FastAPI, Depends, HTTPException, Request, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from .database import SessionLocal, engine, get_db, Base
from .exceptions import form_exception_handler, FormException
from .phones import router as phone_router
from .auth import router as auth_router

Base.metadata.create_all(bind=engine)

        
app = FastAPI()

app.add_exception_handler(FormException, form_exception_handler)

app.include_router(phone_router.router)
app.include_router(auth_router.router)

@app.get('/', response_class=RedirectResponse)
def index():
    return "/phone_book"