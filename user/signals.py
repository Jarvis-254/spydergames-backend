from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from wallet.models import Wallet


user = settings.AUTH_USER_MODEL
# Function run after sender signal
@receiver(post_save, sender=user)
def Create_wallet(sender, instance, created, **kwargs):
    # Instance is the real object something real like <user:Nova/J.A.R.V.I.S>
    if created:
        Wallet.objects.create(user=instance)
        