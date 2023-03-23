CONFIRMATION = 1
PREPARATION = 2
DELIVERY = 3
FINISH = 4
ORDER_STATUS_CHOICES = [
    (CONFIRMATION, 'Ожидает подтверждения'),
    (PREPARATION, 'Готовится'),
    (DELIVERY, 'Передан курьеру'),
    (FINISH, 'Выполнен')
]

CASH = 'CASH'
CARD = 'CARD'
NOT_SET = 'NONE'
PAYMENT_METHOD_CHOICES = [
    (CASH, 'Наличными'),
    (CARD, 'Электронно'),
    (NOT_SET, 'Не указан')
]
