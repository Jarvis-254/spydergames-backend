from django.db import models
from django.conf import settings
from decimal import Decimal

# Create your models here.
User = settings.AUTH_USER_MODEL


class Wallet(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def deposit(self,amount):
        self.balance += Decimal(str(amount))
        self.save()

        Transaction.objects.create(
            wallet=self,
            amount=amount,  
            transaction_type='deposit'
        )

    def deduct(self,amount):
        amount = Decimal(amount)

        if self.balance>=amount:
            self.balance-=amount
            self.save()
            Transaction.objects.create(
                wallet=self,
                amount=amount, 
                transaction_type='payment'

            )
        return True

    def __str__(self):
        return f"{self.user} wallet"

# Transaction Logic Already their
class Transaction(models.Model):
    TRANSACTION_TYPES=(
        ('deposit', 'Deposit'),
        ('payment', 'Payment'),
        ('stake', 'Stake'),
        ('withdraw', 'Withdraw'),
        ('refund', 'Refund'),
    ) 
    # Because of this Reverse_Relationship Class Wallet has a field named wallet
    user              = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    wallet            = models.ForeignKey(Wallet, on_delete=models.CASCADE)# Many to one relationship
    amount            = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type  = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    created_at        = models.DateTimeField(auto_now_add=True)

   
    #return False

    def __str__(self):
        return f"{self.transaction_type} - {self.amount}"
    
    

