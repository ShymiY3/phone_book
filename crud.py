from sqlalchemy.orm import Session
import schemas, models
from exceptions import FormException
from sqlalchemy import or_


def get_phone_book(db: Session, search: str | None = None):
    if not search: 
        return db.query(models.Phone_book).all()
    return db.query(models.Phone_book).filter(
        or_(
            models.Phone_book.first_name.ilike(f'%{search}%'),
            models.Phone_book.last_name.ilike(f'%{search}%'),
            models.Phone_book.tel.ilike(f'%{search}%'),
            models.Phone_book.email.ilike(f'%{search}%'),
        )
    ).all()

def get_phone_book_by_phone(db: Session, tel: str):
    return db.query(models.Phone_book).filter(models.Phone_book.tel == tel).first()


def get_phone_book_by_id(db: Session, entry_id: int):
    return db.query(models.Phone_book).filter(models.Phone_book.id == entry_id).first()

def create_phone_book_entry(db: Session, entry: schemas.PhonebookInput):
    db_entry = models.Phone_book(
        first_name=entry.first_name,
        last_name=entry.last_name,
        tel=entry.tel,
        email=entry.email,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

def update_phone_book_entry(db: Session, entry: schemas.PhonebookUpdate, entry_id: int):
    db_entry = get_phone_book_by_id(db, entry_id)
    if not db_entry:
        raise FormException(status_code=400, detail="Entry not in Phone Book")
    entry_data = entry.dict(exclude_none=True, exclude_unset=True)
    print(entry_data)
    for key, value in entry_data.items():
        setattr(db_entry, key, value)
        
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)


def delete_phone_book_entry(db: Session, entry_id: int):
    db_entry = get_phone_book_by_id(db, entry_id)
    if not db_entry:
        raise FormException(status_code=400, detail="Entry not in Phone Book")
    db.delete(db_entry)
    db.commit()