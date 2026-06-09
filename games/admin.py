from django.contrib import admin
from .models import Match, CompanyWallet
# Register your models here.
@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('player1', 'player2', 'stake', 'status', 'winner')
@admin.register(CompanyWallet)
class CompanyWalletAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance')