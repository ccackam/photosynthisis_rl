import photosynthisis
import agent
import time

print("Let's Play Photosynthisis!")



players = [agent.create(1,0),agent.create(0,1),agent.create(0,2),agent.create(0,3)]

game = photosynthisis.start(True)
game.new_game(len(players))

final_score = None
while final_score == None:
    s = game.get_state()
    a = game.get_actions()
    c = players[game.players_turn].make_decision(s,a)
    final_score = game.take_action(c)
    game.redraw()

print("Good Game!")
