from django.db import models
from django.conf import settings
from decimal import Decimal
import uuid
import random
import string
from django.utils import timezone
from django.db import transaction
from .generator import master_puzzle



User = settings.AUTH_USER_MODEL

class GameStatus(models.TextChoices):
    WAITING   = 'waiting',   'Waiting for Opponent'
    ACTIVE    = 'active',    'In Progress'
    FINISHED  = 'finished',  'Finished'
    ABANDONED = 'abandoned', 'Abandoned'

class Match(models.Model):
    """ Main Logic for the Game everything concerning the game """
    """ It controls everything Player, Stake Game id e.t.c """
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code         = models.CharField(max_length=8, unique=True, db_index=True, null=True, blank=True)
    started_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)
    finished_at  = models.DateTimeField(null=True, blank=True)
    player1      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player1')
    player2      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='player2', null=True, blank=True)
    # Money at stake for you to play
    stake        = models.DecimalField(max_digits=10, decimal_places=2)
    winner       = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True,related_name='winner')
    status       = models.CharField(max_length=20,choices=GameStatus.choices, default=GameStatus.WAITING)
    total_rounds = models.PositiveSmallIntegerField(default=3)
    updated_field= models.TimeField(auto_now=True)

    # Type hint user:User
    """ Fuction Generate random code which will be used to connect to the game by player2 """
    def generate_code(self):
        while True:
            code ="".join(random.choices(string.ascii_uppercase + string.digits, k=8))
            # Cheacking the db for similar code if not found it returns the code 
            if not Match.objects.filter(code=code).exists():
                return code
    """ Code Overriding the save() method """       
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)
# Joining logic for the second player
    
    @classmethod
    def join(cls, code, user):
        try:
            match = cls.objects.get(code=code)
        except cls.DoesNotExist:
            raise ValueError(
            "The code doesn't exist"
        )
        if match.player2 is not None:
            raise ValueError(
            "Game Room Full !!!"
        )
        if match.player1 == user:
            raise ValueError(
            "You can't join your own match."
        )
        if user.wallet.balance < match.stake:
            raise ValueError(
            "Insufficient Balance"
        )
        match.player2 = user
        match.save()
        return match

    def create_round(self, round_number):
        puzzle = master_puzzle()
        return MatchRound.objects.create(
            match = self,
            round_number = round_number,
            numbers = puzzle["numbers"],
            correct_answer = puzzle["answer"],
            category = puzzle["category"]
        )

    def start_match(self):
        """If the balance in each player wallet is sufficient enough then the game starts"""
        """This function checks if each player is allowed to play """

        w1 = self.player1.wallet
        w2 = self.player2.wallet
        if not self.player2:
            raise ValueError(" Can't start match without player2 ")

        if w1.balance < self.stake or w2.balance < self.stake:
            return False
        # transaction.atomic() used as a context manager
        """ With transaction.atomic() if anything throws back an exception error everything rolls back like nothing happend"""
        with transaction.atomic():
            if not w1.deduct(self.stake) or not w2.deduct(self.stake):
                raise ValueError(" Payment failed ")
        
        self.status = GameStatus.ACTIVE
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
        
        """ GameScore for each player """
        """ Each will have it's own row on the database """

        MatchScore.objects.get_or_create(match=self, player=self.player1)
        MatchScore.objects.get_or_create(match=self, player=self.player2)
        self.create_round(round_number=1)
        return True
     
     # Payment logic and end_match logic

    def end_match(self, winner):
        total         = self.stake * 2
        platform_cut  = total * Decimal("0.05")
        winner_amount = total - platform_cut
        company_wallet = CompanyWallet.objects.first()
        if company_wallet:
            company_wallet.deposit(platform_cut)
        winner.wallet.deposit(winner_amount)
        self.winner = winner
        self.status = GameStatus.FINISHED
        self.finished_at = timezone.now()
        self.save()

        return True
    def __str__(self):
        return f"{self.player1} vs {self.player2}"
""" This function handles games per match what game id was played how was the score, what round was being played and all that """
""" Game stat """
class MatchRound(models.Model):
    match          = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='rounds')
    round_number   = models.PositiveBigIntegerField(default=1)
    numbers        = models.JSONField()
    correct_answer = models.IntegerField()
    category       = models.CharField(max_length=10)
    created_at     = models.DateTimeField(auto_now_add=True)
    completed      = models.BooleanField(default=False) # Here it is completed like round completed

    def __str__(self):
        return f"{self.match.code} - Round {self.round_number}"
    
    
class RoundSubmission(models.Model):
    round        = models.ForeignKey(MatchRound, on_delete=models.CASCADE, related_name='submissions')
    player       = models.ForeignKey(User, on_delete=models.CASCADE)
    answer       = models.IntegerField()
    is_correct   = models.BooleanField(default=False)
    submitted_at = models.TimeField(auto_now_add=True)

    class Meta:
        # The unique_together(Only take a list or a tuple so round each player can only answer onces not twice same applies to player)
        unique_together = (
            'round',
            'player'
        )



 # Winner Deciding logic + Money Distributer and Platform takes Decimal(.25)
""" Store each player performance per match """
""" One row per Player Per Match """
""" Overall performance """
class MatchScore(models.Model):
    id     = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    match  = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='scores') # Has access to Match Object
    player = models.ForeignKey(User, on_delete=models.CASCADE)

    # Scoring Logic
    total_points    = models.IntegerField(default=0)
    correct_answers = models.PositiveSmallIntegerField(default=0)
    wrong_answers   = models.PositiveSmallIntegerField(default=0)

    # Speed Tracking
    #total_time_taken = models.FloatField(default=0.0)
    time_taken       = models.FloatField(default=0.0)
    fastest_answer   = models.FloatField(null=True, blank=True)
    slowest_answer   = models.FloatField(null=True, blank=True)

    # Round performance
    rounds_won = models.PositiveSmallIntegerField(default=0)

    # Final Results
    is_winner = models.BooleanField(default=False)

    # Scoring Logic
    def apply_score(self, correct_answers, time_taken):
        self.time_taken = time_taken
        if not correct_answers:
            self.wrong_answers += 1
            self.save()
            return True
        points = 10
        if time_taken <= 2:
            points += 5
        elif time_taken >= 4:
            points += 1

        self.total_points += points
        
        if self.fastest_answer is None or time_taken < self.fastest_answer:
            self.fastest_answer = time_taken
        else:
            if self.slowest_answer is None or time_taken > self.slowest_answer:
                self.slowest_answer = time_taken

        self.save()
# Wallet 
class CompanyWallet(models.Model):
    name    = models.CharField(max_length=100, default="SpyderByte")
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0.00"))

    def deposit(self, amount):
        self.balance +=amount
        self.save()

    def __str__(self):
            return f"{self.name} - {self.balance}"


class Payment(models.Model):
    STATUS_CHOICE = (

        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    )

    user       = models.ForeignKey(User, on_delete=models.CASCADE,)
    amount     = models.DecimalField(max_digits=15, decimal_places=2)
    reference  = models.CharField(max_length=100, unique=True)
    status     = models.CharField(max_length=100, choices=STATUS_CHOICE, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
