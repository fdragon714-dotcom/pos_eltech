from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class MaximumLengthValidator:
    def __init__(self, max_length=15):
        self.max_length = max_length

    def validate(self, password, user=None):
        if len(password) > self.max_length:
            raise ValidationError(
                _("Kata sandi terlalu panjang. Maksimal %(max_length)d karakter."),
                code='password_too_long',
                params={'max_length': self.max_length},
            )

    def get_help_text(self):
        return _("Kata sandi tidak boleh lebih dari %(max_length)d karakter.") % {'max_length': self.max_length}
