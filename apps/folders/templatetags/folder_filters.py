from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='truncate_characters')
# Truncates a string and adds ... if it exceeds a specified limit
# @param value original string
# @param arg max length that the string can be
# @return string within specified char limit
def truncate_characters(value, arg):
    limit = int(arg)
    if not value or len(value) <= limit:
        return value
    return value[:limit] + "..."
