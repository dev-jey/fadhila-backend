from django.db import models
from messenger.apps.authentication.models import User
from messenger.apps.orders.models import Orders

# Create your models here.


class Payments(models.Model):
    '''Defines attributes of the payments model'''
    MODES = [
        ('A', 'Airtel'),
        ('C', 'Cooperative'),
        ('V', 'Visa'),
        ('M', 'Mpesa'),
        ('P', 'Paypal'),
        ('K', 'Krep'),
        ('U', 'Unknown')
    ]
    ref_number = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=False)
    mobile_no = models.CharField(max_length=12)
    payment_mode = models.CharField(
        max_length=1,
        choices=MODES,
        default='',
    )
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    paid_at = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''Defines the ordering of the
         orders if retrieved'''
        ordering = ('created_at',)

    def __str__(self):
        return self.ref_number

class PaymentsTracker(models.Model):
    '''Defines attributes of the payments model'''
    pesapal_merchant_reference = models.CharField(max_length=100)
    pesapal_transaction_tracking_id = models.CharField(max_length=100)
    tracking_number = models.CharField(max_length=100)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.pesapal_merchant_reference