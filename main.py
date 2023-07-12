from fastapi import FastAPI, Depends, HTTPException, Request, status, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import models
from database import SessionLocal, engine
from exceptions import form_exception_handler, FormException
import phonenumbers, crud, schemas

models.Base.metadata.create_all(bind=engine)

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()

def formatPhone(input):
    try:
        return phonenumbers.format_number(phonenumbers.parse(input), phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except:
        return input

templates = Jinja2Templates(directory='templates')
templates.env.filters['formatPhone'] = formatPhone

        
app = FastAPI()

app.add_exception_handler(FormException, form_exception_handler)


@app.get('/', response_model=list[schemas.PhonebookBase], response_class=HTMLResponse)
async def get_Phone_book(request: Request, db: Session = Depends(get_db), search: str | None = None):
    return templates.TemplateResponse('index.html', {"request":request, 'phone_book':crud.get_phone_book(db, search)})
    
    
@app.get('/create', response_class=HTMLResponse)
async def create_entry_form(request: Request):
    return templates.TemplateResponse('create_entry.html', {'request': request})
    
@app.post('/create', response_class=RedirectResponse)
async def create_entry(request: Request, 
                       entry: schemas.PhonebookInput = Depends(schemas.PhonebookInput.as_form), 
                       db: Session = Depends(get_db)):
    entry.clean_entry()
    if not entry.is_valid(db):
         raise FormException(status_code=400, detail="Can't create an entry")
     
    crud.create_phone_book_entry(db=db, entry=entry)
    return RedirectResponse('../?success=True', status.HTTP_302_FOUND)

@app.get('/update/{entry_id}', response_class=HTMLResponse)
async def update_entry(request: Request, entry_id):
    return templates.TemplateResponse('update_entry.html', {'request': request})

@app.post("/update/{entry_id}", response_class=RedirectResponse)
def update_entry(request: Request, 
                entry_id: int, 
                entry: schemas.PhonebookUpdate = Depends(schemas.PhonebookUpdate.as_form), 
                db: Session = Depends(get_db)):
    entry.clean_entry()
    if not entry.is_valid(db):
        raise FormException(status_code=400, detail="Can't update an entry")    
    crud.update_phone_book_entry(db=db, entry=entry, entry_id=entry_id)
    return RedirectResponse('../../?alert=success&mess=Updated Successfully', status_code=status.HTTP_303_SEE_OTHER)

@app.get('/delete/{entry_id}', response_class=HTMLResponse)
async def delete_entry(request: Request, entry_id: int, db: Session = Depends(get_db)):
    return templates.TemplateResponse('delete_entry.html', {'request': request, 'entry':crud.get_phone_book_by_id(db, entry_id).__dict__})

@app.post('/delete/{entry_id}', response_class=RedirectResponse)
async def delete_entry(request: Request, entry_id: int, db: Session = Depends(get_db)):
    crud.delete_phone_book_entry(db, entry_id)
    return RedirectResponse('../../?alert=success&mess=Deleted Successfully', status_code=status.HTTP_303_SEE_OTHER)