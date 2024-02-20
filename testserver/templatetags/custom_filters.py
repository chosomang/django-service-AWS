from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    original, new = arg.split(',')
    return value.replace(original, new)
