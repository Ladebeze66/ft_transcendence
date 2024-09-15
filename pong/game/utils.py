from .models import Player, Tournoi, Match
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Max, Sum, F
from datetime import timedelta
from channels.db import database_sync_to_async

def handle_game_data(p1, p2, s_p1, s_p2, bt_p1, bt_2, dur, is_tournoi, name_tournament):
    try:
        player_1 = get_or_create_player(p1)
        player_2 = get_or_create_player(p2)

        create_match(player_1, player_2, s_p1, s_p2, bt_p1, bt_2, dur, is_tournoi, name_tournament)

        update_player_statistics(p1)
        update_player_statistics(p2)
  
    except Exception as e:
        print(f"Error in endfortheouche: {e}")

def get_player_by_name(name):
    exists = Player.objects.filter(name=name).exists()
    return exists


def get_player(name):
    return Player.objects.get(name=name)


def get_or_create_player(name):
    player_exists = get_player_by_name(name)
    if not player_exists:
        player = create_player(name)
        return player
    else:
        player = get_player(name)
        return player 


def create_player(
    name, 
    total_match=0, 
    total_win=0, 
    p_win= None, 
    m_score_match= None, 
    m_score_adv_match= None, 
    best_score=0, 
    m_nbr_ball_touch= None, 
    total_duration= None, 
    m_duration= None, 
    num_participated_tournaments=0, 
    num_won_tournaments=0
):
    
    player = Player(
        name=name,
        total_match=total_match,
        total_win=total_win,
        p_win=p_win,
        m_score_match=m_score_match,
        m_score_adv_match=m_score_adv_match,
        best_score=best_score,
        m_nbr_ball_touch=m_nbr_ball_touch,
        total_duration=total_duration,
        m_duration=m_duration,
        num_participated_tournaments=num_participated_tournaments,
        num_won_tournaments=num_won_tournaments
    )
    player.save()
    return player

def create_tournoi(name, nbr_player, date, winner):
    tournoi = Tournoi(name=name, nbr_player=nbr_player, date=date, winner=winner)
    tournoi.save()
    return tournoi

def create_match(player1, player2, score_player1, score_player2, nbr_ball_touch_p1, nbr_ball_touch_p2, duration, is_tournoi, tournoi):
    match = Match(
        player1=player1,
        player2=player2,
        score_player1=score_player1,
        score_player2=score_player2,
        nbr_ball_touch_p1=nbr_ball_touch_p1,
        nbr_ball_touch_p2=nbr_ball_touch_p2,
        duration=duration,
        is_tournoi=is_tournoi,
        tournoi=tournoi
    )

    if score_player1 > score_player2:
        match.winner = match.player1
    elif score_player2 > score_player1:
        match.winner = match.player2
    else:
        match.winner = None
    
    match.save()
    return match

def update_player_statistics(player_name):
    player = get_object_or_404(Player, name=player_name)

    matches_as_player1 = Match.objects.filter(player1=player)
    matches_as_player2 = Match.objects.filter(player2=player)

    total_match = matches_as_player1.count() + matches_as_player2.count()
    
    # avoid dividing by 0
    if total_match == 0:
        player.total_match = total_match
        player.total_win = 0
        player.p_win = 0
        player.m_score_match = 0
        player.m_score_adv_match = 0
        player.best_score = 0
        player.m_nbr_ball_touch = 0
        player.total_duration = 0
        player.m_duration = 0
        player.num_participated_tournaments = 0
        player.num_won_tournaments = 0
        player.save()
        return
    
    won_matches = Match.objects.filter(winner=player)
    #part_tourn_as_p1 = Tournoi.objects.filter(matches__is_tournoi=True, matches__matches_as_player1=player)
    #part_tourn_as_p2 = Tournoi.objects.filter(matches__is_tournoi=True, matches__matches_as_player2=player)
    #won_tourn = Tournoi.objects.filter(winner=player) 

    total_score = matches_as_player1.aggregate(Sum('score_player1'))['score_player1__sum'] or 0
    total_score += matches_as_player2.aggregate(Sum('score_player2'))['score_player2__sum'] or 0
    
    total_score_adv = matches_as_player1.aggregate(Sum('score_player2'))['score_player2__sum'] or 0
    total_score_adv += matches_as_player2.aggregate(Sum('score_player1'))['score_player1__sum'] or 0

    total_win = won_matches.count()
    p_win = (total_win / total_match) * 100
    
    m_score_match = total_score / total_match
    m_score_adv_match = total_score_adv / total_match

    nbr_ball_touch = matches_as_player1.aggregate(Sum('nbr_ball_touch_p1'))['nbr_ball_touch_p1__sum'] or 0
    nbr_ball_touch += matches_as_player2.aggregate(Sum('nbr_ball_touch_p2'))['nbr_ball_touch_p2__sum'] or 0
    m_nbr_ball_touch = nbr_ball_touch / total_match

    total_duration = matches_as_player1.aggregate(Sum('duration'))['duration__sum'] or 0
    total_duration += matches_as_player2.aggregate(Sum('duration'))['duration__sum'] or 0
    m_duration = total_duration / total_match

    #total_tourn_p = part_tourn_as_p1.count() + part_tourn_as_p2.count()
    #total_win_tourn = won_tourn.count()
    #p_win_tourn = (total_win_tourn / total_tourn_p) * 100 if total_tourn_p else 0
 
    best_score_as_player1 = matches_as_player1.aggregate(Max('score_player1'))['score_player1__max'] or 0
    best_score_as_player2 = matches_as_player2.aggregate(Max('score_player2'))['score_player2__max'] or 0
    best_score = max(best_score_as_player1, best_score_as_player2)

    player.total_match = total_match
    player.total_win = total_win
    player.p_win = p_win
    player.m_score_match = m_score_match
    player.m_score_adv_match = m_score_adv_match
    player.best_score = best_score
    player.m_nbr_ball_touch = m_nbr_ball_touch
    player.total_duration = total_duration
    player.m_duration = m_duration
    # player.num_participated_tournaments = total_tourn_p
    #player.num_won_tournaments = total_win_tourn 

    player.save()

def get_player_p_win(player_name):
    player = get_object_or_404(Player, name=player_name)
    return player.p_win

def create_tournament(name, nbr_player):
    print("tournoi created!!!")
    tournoi=Tournoi(name=name, nbr_player=nbr_player, winner=None)
    tournoi.save()
    print(f"tournoi name : {tournoi.name}  *******!*!*!*!**!*!**!*!*!*!*!*!*!*!*!*")
    return tournoi

def update_tournament(name_tournoi, winner_name):
    tournoi = get_object_or_404(Tournoi, name=name_tournoi)
    winner_p = get_object_or_404(Player, name=winner_name)
    print(f"in update tourna - tournoi name : {tournoi.name}  *******!*!*!*!**!*!**!*!*!*!*!*!*!*!*!*")
    print(f"in update tourna - winner is : {winner_p.name}  *******!*!*!*!**!*!**!*!*!*!*!*!*!*!*!*")

    tournoi.winner = winner_p
    print(f"in update tourna - TOURNOI winner is : {tournoi.winner.name}  *******!*!*!*!**!*!**!*!*!*!*!*!*!*!*!*")
    tournoi.save()




def getlen():
    return Tournoi.objects.count()
