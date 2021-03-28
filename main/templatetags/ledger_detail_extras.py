from django import template
from django.http import QueryDict

register = template.Library()

@register.filter
def multiply(val1,val2):
    try:
        return val1 * val2
    except:
        return -1