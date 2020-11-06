import timeit

mysetup = """
import photosynthisis
import agent
# import DQN
import neural_network
import numpy as np
import random
import time

def phi_(s):
    state_memory = 24
    s_0 = s[0]

    phi = np.tile(s_0,(state_memory,1))
    phi_index = len(phi)-1
    for count,state_number in enumerate(reversed(range(len(s)))):
        for state in np.flipud(s[state_number]):
            phi[phi_index] = state
            phi_index -= 1
            if phi_index <0:
                break
        if phi_index <0:
            break

    # print(len(phi))
    return phi

def select_best_action(a,expected_reward,epsilon):
    weights = np.zeros(len(a))

    largest_index = -1
    largest = -1
    for i,action in enumerate(a):
        if np.isfinite(action):
            weights[i] = 1
            if expected_reward[i] > largest:
                largest = expected_reward[i]
                largest_index = i

    finite_count = np.sum(weights)
    if finite_count>1:
        weights = weights*(hyper_parameters["epsilon"]/(finite_count-1))

    weights[largest_index] = 1-epsilon

    choices = range(len(a))
    choosen_action = random.choices(choices,weights=weights)[0]
    return choosen_action

hyper_parameters = {"size":{0:2160,1:1080,2:540,3:42},"m":16,"activation":{1:"Leaky ReLU",2:"Leaky ReLU",3:"linear"},"alpha":0.0001,"epsilon":1/50,"gamma":0.1}
allowable_players = [2,3,4]

game = photosynthisis.start(False)

D = []
Q = neural_network.initilize(hyper_parameters)
"""

mycode = """

players = []
for i in range(np.random.choice(allowable_players)):
    if not i:
        type = 3
    else:
        type = np.random.randint(0,2)
    players.append(agent.create(type,i))
game.new_game(len(players))

s = [game.get_state()]
phi = phi_(s)

final_score = None
while final_score == None:
    a = game.get_actions()
    if game.players_turn:
        c = players[game.players_turn].make_decision(s[-1],a)
    else:
        expected_reward = Q.forward_prop(phi)
        c = select_best_action(a,expected_reward,hyper_parameters["epsilon"])

    final_score = game.take_action(c)
    if ((not game.players_turn) and c==0) or (final_score != None):
        if final_score != None:
            other_best = np.max(final_score[1:])
            r = (final_score[0]-other_best)/1000
        else:
            r = 0

        s.append(game.get_state())
        phi_new = phi_(s)

        D.append((phi,r,a,c,phi_new))
        # print(len(D))



        xs = np.tile(phi,(1,hyper_parameters["m"]))
        xs2 = np.tile(phi,(1,hyper_parameters["m"]))
        rs = np.zeros((1,hyper_parameters["m"]))
        cs = np.zeros((1,hyper_parameters["m"]))
        az = np.tile(a,(1,hyper_parameters["m"]))
        for j in range(hyper_parameters["m"]):
            sample_index = np.random.choice(range(len(D)))
            sample_phi_old,sample_r,sample_a,sample_c,sample_phi_new = D[sample_index]
            for k in range(len(phi)):
                xs[k,j] = sample_phi_old[k]
                xs2[k,j] = sample_phi_new[k]
            rs[0,j] = sample_r
            cs[0,j] = sample_c
            for k in range(len(a)):
                # print(az)
                # print(sample_a)
                # print(k,j)
                az[k,j] = sample_a[k,0]
        qs = Q.forward_prop(xs)
        qs2 = Q.forward_prop(xs2)
        y = rs.copy()
        y_hat = rs.copy()
        for j in range(hyper_parameters["m"]):
            best_action = select_best_action(az[:,j],qs2[:,j],0)
            E_q = qs2[best_action,j]
            if y[0,j] == 0:
                y[0,j] = hyper_parameters["gamma"]*E_q
            y_hat[0,j] = qs[int(cs[0,j]),j]
        dL_dyhat = y - y_hat

        Q.backward_prop(dL_dyhat)

        phi = phi_new
"""

print(timeit.timeit(setup = mysetup,
                    stmt = mycode,
                    number = 10))





# import timeit
#
# mysetup = """
# import photosynthisis
# import agent
# import numpy as np
# import random
#
# # random.seed(10)
# # print("Let's Play Photosynthisis!")
#
# allowable_players = [2,3,4]
#
# game = photosynthisis.start(False)
#
# """
#
# mycode = """
#
# # for throw in range(100):
# players = []
# for i in range(np.random.choice(allowable_players)):
#     players.append(agent.create(1,i,random.randint(0,100)))
# game.new_game(len(players))
# final_score = None
# while final_score == None:
#     s = game.get_state()
#     a = game.get_actions()
#     c = players[game.players_turn].make_decision(s,a)
#     final_score = game.take_action(c)
# """
#
# print(timeit.timeit(setup = mysetup,
#                     stmt = mycode,
#                     number = 100))
