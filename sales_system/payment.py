from collections import namedtuple
from sales_system.exceptions import CardError, PaymentError, CurrencyError


PaymentResult = namedtuple('PaymentResult', ('amount', 'currency'))


class PaymentGateway:
    SUPPORTED_CURRENCIES = ('EUR',)

    def charge(self, amount, token, currency='EUR'):
        if token == 'card_error':
            raise CardError("Your card has been declined")
        elif token == 'payment_error':
            raise PaymentError("Something went wrong with your transaction")
        elif currency not in self.SUPPORTED_CURRENCIES:
            raise CurrencyError(f"Currency {currency} not supported")
        else:
            return PaymentResult(amount, currency)
