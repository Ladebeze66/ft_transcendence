from .models import Player, Tournoi, Match
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Max, Sum, F
from datetime import timedelta
from channels.db import database_sync_to_async

async def endfortheouche(p1, p2, s_p1, s_p2, bt_p1, bt_2, dur, is_tournoi, name_tournament):
    # Check if player p1 exists, if not create
    if not await database_sync_to_async(Player.objects.filter(name=p1).exists)():
        player_1 = await create_player(p1)
        print("############# PLAYER DONE")
    else:
        player_1 = await database_sync_to_async(Player.objects.get)(name=p1)

    # Check if player p2 exists, if not create
    if not await database_sync_to_async(Player.objects.filter(name=p2).exists)():
        player_2 = await create_player(p2)
        print("############# PLAYER DONE")
    else:
        player_2 = await database_sync_to_async(Player.objects.get)(name=p2)
    
    # create Match
    print("############# BEFORE MATCH")
    await create_match(player_1, player_2, s_p1, s_p2, bt_p1, bt_2, dur, is_tournoi, name_tournament)
    print("############# AFTER DONE")

    # Update data p1 et p2
    
    await uptdate_player_statistics(p1)
    print("############# END STAT P1")
    await uptdate_player_statistics(p2)

@database_sync_to_async
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
    if Player.objects.filter(name=name).exists():
        raise ValueError(f"A player with the name '{name}' already exists.")

    player = Player(
        name=name,
        total_match  = total_match,
        total_win = total_win,
        p_win = p_win,
        m_score_match = m_score_match,
        m_score_adv_match = m_score_adv_match,
        best_score = best_score,
        m_nbr_ball_touch = m_nbr_ball_touch,
        total_duration = total_duration,
        m_duration = m_duration,
        num_participated_tournaments = num_participated_tournaments,
        num_won_tournaments = num_won_tournaments
    )
    player.save()
    return player

@database_sync_to_async
def create_tournoi(name, nbr_player, date, winner):
    tournoi = Tournoi(name=name, nbr_player=nbr_player, date=date, winner=winner)
    tournoi.save()
    return tournoi

@database_sync_to_async
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

@database_sync_to_async
def uptdate_player_statistics(player_name):
    print("############# BEG STAT P")
    player = get_object_or_404(Player, name=player_name)

    # Filtrer les matchs où le joueur est joueur 1 ou joueur 2
    print("############# HERE")
    matches_as_player1 = Match.objects.filter(player1=player)
    matches_as_player2 = Match.objects.filter(player2=player)
    print("############# ACTUALLY, IT'S GOOD")

    # Calculer les statistiques
    total_match = matches_as_player1.count() + matches_as_player2.count()
    
    if total_match == 0:
        # Eviter la division par zéro
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
    """ part_tourn_as_p1 = Tournoi.objects.filter(matches__is_tournoi=True, matches__matches_as_player1=player)
    part_tourn_as_p2 = Tournoi.objects.filter(matches__is_tournoi=True, matches__matches_as_player2=player)
    won_tourn = Tournoi.objects.filter(winner=player) """

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

    """ total_tourn_p = part_tourn_as_p1.count() + part_tourn_as_p2.count()
    total_win_tourn = won_tourn.count()
    p_win_tourn = (total_win_tourn / total_tourn_p) * 100 if total_tourn_p else 0
 """
    best_score_as_player1 = matches_as_player1.aggregate(Max('score_player1'))['score_player1__max'] or 0
    best_score_as_player2 = matches_as_player2.aggregate(Max('score_player2'))['score_player2__max'] or 0
    best_score = max(best_score_as_player1, best_score_as_player2)

    # Mettre à jour les champs du joueur
    player.total_match = total_match
    player.total_win = total_win
    player.p_win = p_win
    player.m_score_match = m_score_match
    player.m_score_adv_match = m_score_adv_match
    player.best_score = best_score
    player.m_nbr_ball_touch = m_nbr_ball_touch
    player.total_duration = total_duration
    player.m_duration = m_duration
    """ player.num_participated_tournaments = total_tourn_p
    player.num_won_tournaments = total_win_tourn """

    player.save()
    print("CHAKU IS THE BEST")

def get_player_p_win(player_name):
    # Rechercher le joueur par son nom
    player = get_object_or_404(Player, name=player_name)
    # Retourner la valeur de p_win
    return player.p_win


""" def complete_match(match_id, score_player1, score_player2, nbr_ball_touch_p1, nbr_ball_touch_p2, duration):
    try:
        match = Match.objects.get(id=match_id)
    except Match.DoesNotExist:
        raise ValidationError(f"Match with id {match_id} does not exist")

    match.score_player1 = score_player1
    match.score_player2 = score_player2
    match.nbr_ball_touch_p1 = nbr_ball_touch_p1
    match.nbr_ball_touch_p2 = nbr_ball_touch_p2
    match.duration = duration

    if score_player1 > score_player2:
        match.winner = match.player1
    elif score_player2 > score_player1:
        match.winner = match.player2
    else:
        match.winner = None

    match.save()
    return match """

""" def complete_tournoi(tournoi_id, player):
    try:
        tournoi = Tournoi.objects.get(id = tournoi_id)
    except Tournoi.DoesNotExist:
        raise ValidationError(f"Tournoi with id {tournoi_id} does not exist")
    
    tournoi.winner = player
    tournoi.save()
    return tournoi """


    
