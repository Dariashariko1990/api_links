from django.core.exceptions import ValidationError
import validators


def domain_validator(url):
    """ Validates domain name.
    :param url: link
    :raise Validation Error
    :return None
    """
    if not validators.domain(url):
        raise ValidationError("Невалидный домен.")
