from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security.utils import get_authorization_scheme_param 
from sqlalchemy.orm import Session
from ..database import get_db
from ..exceptions import FormException
from .custom_filters import formatPhone
from . import crud, schemas
from fastapi.templating import Jinja2Templates
import os
from ..auth.crud import get_current_user_from_token
from ..auth.models import User

router = APIRouter(prefix="/phone_book", tags=["PHONE_BOOK"])

templates = Jinja2Templates(
    directory=os.path.join(os.getcwd(), "phone_book", "templates")
)
templates.env.filters["formatPhone"] = formatPhone


@router.get(
    "/", response_model=list[schemas.PhonebookBase], response_class=HTMLResponse
)
async def get_Phone_book(
    request: Request, db: Session = Depends(get_db), search: str | None = None
):
    print(request.headers.get("Authorization"))
    try:
        token = request.cookies.get("access_token")
        _, param = get_authorization_scheme_param(token)  # scheme will hold "Bearer" and param will hold actual token value
        user = get_current_user_from_token(param, db)
        user_id = user.id
    except:
        user_id = ''
    return templates.TemplateResponse(
        "phones/index.html",
        {"request": request, "phone_book": crud.get_phone_book(db, search), 'user_id':user_id},
    )


@router.get("/create", response_class=HTMLResponse)
async def create_entry_form(
    request: Request, user: User = Depends(get_current_user_from_token)
):
    return templates.TemplateResponse("phones/create_entry.html", {"request": request})


@router.post("/create", response_class=RedirectResponse)
async def create_entry(
    request: Request,
    entry: schemas.PhonebookInput = Depends(schemas.PhonebookInput.as_form),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    entry.author_id = user.id 
    entry.clean_entry()
    if not entry.is_valid(db):
        raise FormException(status_code=400, detail="Can't create an entry")

    crud.create_phone_book_entry(db=db, entry=entry)
    return RedirectResponse(
        "../?alert=success&mess=Created Successfully", status.HTTP_302_FOUND
    )


@router.get("/update/{entry_id}", response_class=HTMLResponse)
async def update_entry(
    request: Request, entry_id: int, user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)
):
    if crud.get_phone_book_by_id(db, entry_id).author_id != user.id:
        return RedirectResponse(f"../?alert=danger&mess=Can't update that entry", status_code=status.HTTP_302_FOUND, )
    return templates.TemplateResponse("phones/update_entry.html", {"request": request})


@router.post("/update/{entry_id}", response_class=RedirectResponse)
def update_entry(
    request: Request,
    entry_id: int,
    entry: schemas.PhonebookUpdate = Depends(schemas.PhonebookUpdate.as_form),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    if crud.get_phone_book_by_id(db, entry_id).author_id != user.id:
        return RedirectResponse(f"../?alert=danger&mess=Can't update that entry", status_code=status.HTTP_302_FOUND, )
    entry.clean_entry()
    if not entry.is_valid(db):
        raise FormException(status_code=400, detail="Can't update an entry")
    crud.update_phone_book_entry(db=db, entry=entry, entry_id=entry_id)
    return RedirectResponse(
        "../?alert=success&mess=Updated Successfully",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/delete/{entry_id}", response_class=HTMLResponse)
async def delete_entry(
    request: Request,
    entry_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    if crud.get_phone_book_by_id(db, entry_id).author_id != user.id:
        return RedirectResponse(f"../?alert=danger&mess=Can't delete that entry", status_code=status.HTTP_302_FOUND, )
    return templates.TemplateResponse(
        "phones/delete_entry.html",
        {"request": request, "entry": crud.get_phone_book_by_id(db, entry_id).__dict__},
    )


@router.post("/delete/{entry_id}", response_class=RedirectResponse)
async def delete_entry(
    request: Request,
    entry_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_from_token),
):
    if crud.get_phone_book_by_id(db, entry_id).author_id != user.id:
        return RedirectResponse(f"../?alert=danger&mess=Can't delete that entry", status_code=status.HTTP_302_FOUND, )
    crud.delete_phone_book_entry(db, entry_id)
    return RedirectResponse(
        "../?alert=success&mess=Deleted Successfully",
        status_code=status.HTTP_303_SEE_OTHER,
    )
