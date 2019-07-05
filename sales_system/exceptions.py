class PaymentError(Exception):
    pass


class CurrencyError(PaymentError):
    pass


class CardError(PaymentError):
    pass


class TicketSystemError(Exception):
    pass


class InvalidTicket(TicketSystemError):
    pass


class ConnectionNotProvided(TicketSystemError):
    pass
