from django import template

register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)

@register.filter
def get_file_extension(filename):
    try:
        return filename.split('.')[-1].upper()
    except (AttributeError, IndexError):
        return ''