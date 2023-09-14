from django import template
from django.template.defaultfilters import stringfilter
import math

register = template.Library()

@register.filter(name='div')
def div(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter(name='mul')
def mul(value, arg):
    return math.ceil(value * arg * 10)/10