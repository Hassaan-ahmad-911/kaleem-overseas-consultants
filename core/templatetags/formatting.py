from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def pkr(value):
    """Format a price as Pakistani rupees: 45000 -> "PKR 45,000", 1250.5 -> "PKR 1,250.50"."""
    if value in (None, ""):
        return ""
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value
    if amount == amount.to_integral_value():
        return f"PKR {amount:,.0f}"
    return f"PKR {amount:,.2f}"
