import re
from django.core.exceptions import ValidationError

def customer_tax_code_validator(tax_code):
    if re.search("[0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9][0-9]-[0-9][0-9]", tax_code) is None:
        raise ValidationError("Nip powinien mieć format XX-XXX-XXX-XX")


def positive_number_validator(number):
    if int(number) < 0:
        raise ValidationError("Wartość musi być większa od 0")