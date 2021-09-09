from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from api.validators import domain_validator
from urllib.parse import urlparse


def validate(url):
    """ Validates that url is either proper url or proper domain name.
        :param url: link
        :raise Validation Error
        :return Boolean
    """
    try:
        val = URLValidator()
        val(url)
        return True
    except ValidationError:
        try:
            domain_validator(url)
            return True
        except ValidationError:
            return False


def extract_domain(url):
    """ Extract domain name from url.
        :param url: link
        :return domain
    """
    parsed = urlparse(url)
    domain = url.split('/')[0] if parsed.netloc == '' else parsed.netloc
    return domain
