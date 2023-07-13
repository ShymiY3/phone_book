import phonenumbers

def formatPhone(input):
    try:
        return phonenumbers.format_number(phonenumbers.parse(input), phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except:
        return input
