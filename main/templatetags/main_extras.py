from django import template
from django.http import QueryDict

register = template.Library()

@register.filter
def total(value):
    try:
        sum=0.0
        for order in value.orders.all():
            sum += order.items.amount * float(order.items.item.price)            # sum+=float(item.price)
        return sum
    except:
        return -1

@register.filter
def multiply(val1,val2):
    try:
        return val1 * val2
    except:
        return -1


@register.filter
def removefirst(value,start):
    try:
        return value[start:len(value)]
    except:
        return ""