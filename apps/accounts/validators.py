from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class FlexiblePasswordValidator:
    """
    A flexible password validator that allows any password format.
    This validator only ensures the password is not empty and has a minimum length of 1.
    """
    
    def __init__(self, min_length=1):
        self.min_length = min_length
    
    def validate(self, password, user=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must be at least %(min_length)d character long."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )
    
    def get_help_text(self):
        return _("Your password can be any combination of characters, numbers, or symbols.")


class NoRestrictionPasswordValidator:
    """
    A password validator that imposes no restrictions on password format.
    Allows passwords with only numbers, only letters, or any combination.
    """
    
    def __init__(self, min_length=1):
        self.min_length = min_length
    
    def validate(self, password, user=None):
        if not password:
            raise ValidationError(
                _("Password cannot be empty."),
                code='password_empty',
            )
        
        if len(password) < self.min_length:
            raise ValidationError(
                _("Password must be at least %(min_length)d character long."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )
    
    def get_help_text(self):
        return _("Your password can be any combination of characters. No restrictions apply.")
