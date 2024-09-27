from django.db import models


class MpesaTransaction(models.Model):
    transaction_id = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    recipient = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    transaction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_id} - Ksh{self.amount} to {self.recipient}"
    