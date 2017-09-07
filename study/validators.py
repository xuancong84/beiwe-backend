from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible


@deconstructible
class LengthValidator(object):
    length = None  # If length is None, no validation is done
    message = 'Invalid length'
    code = 'invalid'

    def __init__(self, length=None, message=None, code=None):
        if length is not None:
            self.length = length
        if message is None:
            self.message = 'Ensure this value has exactly {} characters.'.format(self.length)
        else:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        """
        Validate that the input is of the proper length, otherwise raise ValidationError.
        """
        if self.length is not None and len(value) != self.length:
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other):
        return (
            isinstance(other, LengthValidator)
            and self.length == other.length
            and self.message == other.message
            and self.code == other.code
        )

    def __ne__(self, other):
        return not (self == other)


# This validator is used by a CharField in the Study model to ensure that the encryption
# key is of the proper length. If the encryption key is changed, be sure to modify the
# validator accordingly.
length_32_validator = LengthValidator(32)

# These validators are used by CharFields in the Researcher and Participant models to ensure
# that those fields' values fit the given regex. The max length requirement is handled by
# the CharField, but the validator ensures that only certain characters are present
# in the field value. If the ID or hashes are changed, be sure to modify or create a new
# validator accordingly.
id_validator = RegexValidator('^[1-9a-z]+$', message='This field can only contain characters 1-9 and a-z.')
# Base 64 encodings can end in up to two = symbols for padding.
url_safe_base_64_validator = RegexValidator('^[0-9a-zA-Z_\-]+={0,2}$')
standard_base_64_validator = RegexValidator('^[0-9a-zA-Z+/]+={0,2}$')
