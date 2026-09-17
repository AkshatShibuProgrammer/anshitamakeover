from django import template
register = template.Library()

@register.filter
def apply_discount(total, discount_percent):
    return float(total) * (float(discount_percent) / 100)
