from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib import messages
from .models import Match
from .serializer import *
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import GameStatus
from .models import RoundSubmission
# Create your views here.

@api_view(["GET","POST"])
@permission_classes([IsAuthenticated])
def create_match_api(request):
    if request.method == "GET":
        return Response({
            "message": "Use POST to create match"
        })
    stake = request.data.get("stake")
    match = Match.objects.create(
        player1 = request.user,
        stake   = stake,
    )
    
    print(match.player1)
    print(match.stake)

    return Response({
        "code": match.code
    })

@api_view(["POST"])
@permission_classes([IsAuthenticated])

def join_match_api(request):
    try:
        code = request.data.get("code")

        print(request.user)
        print(code)

        match = Match.join(
            code=code,
            user=request.user
        )
        match.start_match()
        return Response({

            "code": match.code,
            "status": "joined"

        })

    except Exception as e:
        return Response({
            "error": str(e)
        }, status=400)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def waiting_room_api(request, code): 
    try:
        match = Match.objects.get(code=code)
        return Response({
            "player2_joined": match.player2 is not None,
            "status": match.status,
        })

    except Match.DoesNotExist:
        return Response(
            {"error": "Match not found"},
            status=404
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def game_room_api(request, code):
    match = Match.objects.get(code=code)
    round = match.rounds.last()

    print(round)
    print(round.numbers)
    print(round.category)

    round_serializer = MatchRoundSerializer(round)
    score = match.scores.get(player=request.user)
    score_serializer = MatchScoreSerializer(score)

    return Response({
        "id": round.id,
        "round": round_serializer.data,
        "score": score_serializer.data,
    })

# --Help-- -> AI

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_answer_api(request, code):
    try:
        answer = int(request.data.get("answer"))
        match = Match.objects.get(code=code)  #-->Match object created -->

        current_round = (match.rounds.last())

        if current_round is None:
            return Response({
                "error" : "No active round"
            }, status=400)
        if RoundSubmission.objects.filter(
            round=current_round, # Only one user can answer a round if she/he has the right answer then we should create a second round
            player=request.user # Any player which have loged in should play
            
        ).exists():
            return Response({
                "error" : "You already answered"
            }, status=400)
        
        correct = (
            answer == current_round.correct_answer # --> Need further clarification -->
        )
        # On submission we create a new rounds submission object -->
        submissions = (
            RoundSubmission.objects.create(
                round=current_round,
                player=request.user,
                answer=answer,
                is_correct=correct
            )
        )
        score = (
            match.scores.get(player=request.user)
        )
        score.apply_score(
            correct_answers=correct,
            time_taken=2
        )

        total_answers = (current_round.submissions.count())

        if total_answers < 2:
            return Response({
                "message": "Waiting for opponent",
                "waiting": True
            })

        current_round.completed = True
        current_round.save()

        next_round_number = (
            current_round.round_number + 1
        )
        if next_round_number <= match.total_rounds:
            match.create_round(round_number = next_round_number)
            return Response({
                "message": "Next Round",
                "waiting": False,
                "finished": False
            })
        

        # FINISH MATCH Scoring logic -->
        # Player is request.user (Who ever log's in -->)

        score1 = match.scores.get(
            player=match.player1
        )
        score2 = match.scores.get(
            player=match.player2
        )
        if score1.total_points > score2.total_points:
            winner = match.player1
        elif score2.total_points > score1.total_points:
            winner = match.player2
            # Breaking the tire --> Using time_taken to answer the questions
        else:
            if score1.time_taken < score2.time_taken:
                winner = match.player1
            else:
                if score2.time_taken > score1.time_taken:
                    winner = match.player2

# Ending match if the games is done -->
 
        if winner:
            match.end_match(winner)

        else:
            match.status = (
                GameStatus.FINISHED
            )
            match.save()
        return Response({
            "finished": True,
            "winner": winner.username
            if winner else "Draw" # Conditional Expression(Ternary operator -->)
        })

    except Exception as e:
        return Response({
            "error": str(e)
        }, status=400)
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def results_api(request, code):
    match = Match.objects.get(code=code)
    score1 = match.scores.get(player=match.player1)
    score2 = match.scores.get(player=match.player2)

    return Response({
        "status": match.status,
        "winner":
            match.winner.username
            if match.winner else "Draw", # Conditional expression / Ternary Operator
        "player1": {
            "username": match.player1.username,
            "points": score1.total_points
        },
        "player2": {
            "username": match.player2.username,
            "points": score2.total_points
        },
        "winner_amount" : str(winner_amount),
    })

from .models import Payment
import uuid
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse
from wallet.models import Transaction
from payment.service import PesaPalService

#--> Deposit Api -->
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deposit_api(request):
    amount = request.data.get("amount")
    checkout_url = PesaPalService.create_order(
        user = request.user,
        amount = amount
    )
    return Response({
        "checkout _url" : checkout_url
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def payment_api(request):
    amount = request.data.get("amount")

    payment = Payment.objects.create(
        user = request.user,
        amount = amount,
        reference = str(uuid.uuid4()),
    )
    # --> Request sent to PesaPal(This uuid this is the unique payment)
    return Response({
        "reference" : payment.reference,
        }
    )

@csrf_exempt
def pesapal_callback_api(request):
    reference = request.POST.get("reference")
    payment   = Payment.objects.get(
        reference = reference
    )
    if payment.status == "completed":
        return HttpResponse("OK")
    
    payment.status = "completed"
    payment.save()
# Deposit into the wallet-->
    wallet = payment.user.wallet
    wallet.deposit(payment.amount)

    Transaction.objects.create(
        user             = payment.user, 
        amount           = payment.amount,
        transaction_type = "deposit",
    )
    return HttpResponse("OK")



