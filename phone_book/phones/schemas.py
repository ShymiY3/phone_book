from pydantic import BaseModel, EmailStr
from fastapi import Form
import phonenumbers
from ..exceptions import FormException
from . import crud


class PhonebookBase(BaseModel):
    first_name: str
    last_name: str
    tel: str
    email: EmailStr | None = None
    
class PhonebookInput(PhonebookBase):
    @classmethod
    def as_form(
        cls,
        first_name: str = Form(...),
        last_name: str = Form(...),
        tel: str = Form(...),
        email: EmailStr = Form(None)
    ):
        return cls(
            first_name=first_name,
            last_name=last_name,
            tel=tel,
            email=email
        )
    
    def clean_entry(self):
        if self.tel:
            tel = self.tel.replace(' ','').replace('-','') 
            if len(tel) > 9: 
                if not tel.startswith('+'): 
                    tel = '+' + tel
            else:
                tel = '+48' + tel
            self.tel = tel
            
        if self.first_name:
            self.first_name = self.first_name.strip().title()
            
        if self.last_name:
            self.last_name = self.last_name.strip().title()
    
        return self
    
    def is_valid(self, db):
        if self.tel:
            try:
                if not phonenumbers.is_valid_number(phonenumbers.parse(self.tel)):
                    raise FormException(status_code=400, detail="Invalid Phone number")
            except:
                raise FormException(status_code=400, detail="Invalid Phone number")
            
            db_entry = crud.get_phone_book_by_phone(db, tel=self.tel)
            if db_entry:
                raise FormException(status_code=400, detail="Phone number already in phone book")
        return True
        
class PhonebookUpdate(PhonebookInput):
    first_name: str | None = None
    last_name: str | None = None
    tel: str | None = None
    email: EmailStr | None = None
    
    @classmethod
    def as_form(
        cls,
        first_name: str = Form(None),
        last_name: str = Form(None),
        tel: str = Form(None),
        email: EmailStr = Form(None)
    ):
        return cls(
            first_name=first_name,
            last_name=last_name,
            tel=tel,
            email=email
        )
       