"""
Multi-Currency Exchange Rate Utility
Provides reliable currency conversion for international FMCG quotes.
"""

from typing import Dict, Any


DEFAULT_EXCHANGE_RATES = {
    "INR": 1.0,
    "USD": 0.012,
    "EUR": 0.011,
    "GBP": 0.0095,
    "AED": 0.044,
    "SGD": 0.016,
    "JPY": 1.78
}

CURRENCY_SYMBOLS = {
    "INR": "₹",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "AED": "AED ",
    "SGD": "S$",
    "JPY": "¥"
}


def convert_currency(amount_inr: float, target_currency: str = "USD") -> float:
    """Convert INR amount into target currency using predefined standard rates."""
    target_currency = target_currency.upper()
    rate = DEFAULT_EXCHANGE_RATES.get(target_currency, 1.0)
    return round(amount_inr * rate, 2)


def format_currency_amount(amount: float, currency: str = "INR") -> str:
    """Format numeric amount with proper currency symbol and commas."""
    currency = currency.upper()
    sym = CURRENCY_SYMBOLS.get(currency, f"{currency} ")
    if currency == "INR":
        return f"{sym}{amount:,.2f}"
    return f"{sym}{amount:,.2f}"


def get_supported_currencies() -> Dict[str, float]:
    """Return dictionary of supported target currencies and their relative exchange rates against INR."""
    return DEFAULT_EXCHANGE_RATES.copy()
