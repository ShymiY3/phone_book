from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..exceptions import FormException
from .custom_filters import formatPhone
from . import crud, schemas
from fastapi.templating import Jinja2Templates
import os

router = APIRouter(prefix='/phone_book')

print(os.getcwd())
templates = Jinja2Templates(directory=os.path.join(os.getcwd(), 'phone_book', 'templates'))
templates.env.filters['formatPhone'] = formatPhone


@router.get('/', response_model=list[schemas.PhonebookBase], response_class=HTMLResponse)
async def get_Phone_book(request: Request, db: Session = Depends(get_db), search: str | None = None):
    return templates.TemplateResponse('phones/index.html', {"request":request, 'phone_book':crud.get_phone_book(db, search)})
    
    
@router.get('/create', response_class=HTMLResponse)
async def create_entry_form(request: Request):
    return templates.TemplateResponse('phones/create_entry.html', {'request': request})
    
@router.post('/create', response_class=RedirectResponse)
async def create_entry(request: Request, 
                       entry: schemas.PhonebookInput = Depends(schemas.PhonebookInput.as_form), 
                       db: Session = Depends(get_db)):
    entry.clean_entry()
    if not entry.is_valid(db):
         raise FormException(status_code=400, detail="Can't create an entry")
     
    crud.create_phone_book_entry(db=db, entry=entry)
    return RedirectResponse('../?success=True', status.HTTP_302_FOUND)

@router.get('/update/{entry_id}', response_class=HTMLResponse)
async def update_entry(request: Request, entry_id):
    return templates.TemplateResponse('phones/update_entry.html', {'request': request})

@router.post("/update/{entry_id}", response_class=RedirectResponse)
def update_entry(request: Request, 
                entry_id: int, 
                entry: schemas.PhonebookUpdate = Depends(schemas.PhonebookUpdate.as_form), 
                db: Session = Depends(get_db)):
    entry.clean_entry()
    if not entry.is_valid(db):
        raise FormException(status_code=400, detail="Can't update an entry")    
    crud.update_phone_book_entry(db=db, entry=entry, entry_id=entry_id)
    return RedirectResponse('../?alert=success&mess=Updated Successfully', status_code=status.HTTP_303_SEE_OTHER)

@router.get('/delete/{entry_id}', response_class=HTMLResponse)
async def delete_entry(request: Request, entry_id: int, db: Session = Depends(get_db)):
    return templates.TemplateResponse('phones/delete_entry.html', {'request': request, 'entry':crud.get_phone_book_by_id(db, entry_id).__dict__})

@router.post('/delete/{entry_id}', response_class=RedirectResponse)
async def delete_entry(request: Request, entry_id: int, db: Session = Depends(get_db)):
    crud.delete_phone_book_entry(db, entry_id)
    return RedirectResponse('../?alert=success&mess=Deleted Successfully', status_code=status.HTTP_303_SEE_OTHER)