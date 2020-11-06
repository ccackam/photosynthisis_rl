import numpy as  np
import time
import random

class create:
    # type 0: truely random, 1: guided random, 2: Old AI, 4: person
    # ID
    # color
    color_options = ["Red","Green","Blue","Yellow"]
    epsilon = 0.01

    def __init__(self,type,ID,seed=1):
        # random.seed(seed)
        # np.random.seed(100)
        self.type = type
        self.ID = ID
        self.color = self.color_options[self.ID]
        # print("Player {} is: {}".format(self.ID,self.color))
        self.focus_on_level = np.random.normal(loc=2,scale=1)
        self.focus_on_grow = np.random.normal(loc=12,scale=1)
        # print(ID)
        # print(self.focus_on_level)
        # print(self.focus_on_grow)
        # raise

    def make_decision(self,state,actions):
        choosen_action = 0
        choices = range(len(actions))
        # print("---------------")
        # print(actions)
        if self.type == 0:
            weights = np.ones(len(actions))
            for i,action in enumerate(actions):
                if not np.isfinite(action):
                    weights[i] = 0
            choosen_action = random.choices(choices,weights = weights)[0]
        elif self.type == 1:
            turns_left = state[83,0]
            weights = np.zeros(len(actions))
            # print(turns_left)
            for i,action in enumerate(actions):
                if np.isfinite(action):
                    if 1 <= i and i <= 37:
                        level = state[i-1,0]
                    elif 37 < i:
                        level = i - 37
                    else:
                        level = 0
                    if turns_left<=18 and turns_left>1:
                        # print(level*self.focus_on_level*np.minimum(1,(18-turns_left)/12))
                        weights[i] += np.maximum(0,level*self.focus_on_level*np.minimum(1,(18-turns_left)/12))
                        if 1 <= i and i <= 37:
                            weights[i] += np.maximum(0,self.focus_on_grow*np.minimum(1,(18-turns_left)/12))
                    elif turns_left==1:
                        if (level == 4) and (1 <= i and i <= 37):
                            weights[i] = 1
                    else:
                        weights[i] = 1

            if sum(weights)==0:
                weights[0] = 1

            choosen_action = random.choices(choices,weights=weights)[0]

        elif self.type == 2:
            pass
        elif self.type == 3:
            valid_choice = False
            while not valid_choice:
                print(self.color + "'s Turn: ")
                print("Game Details:    Turns Remaining: {0:2}    Initial Setup: {6:2}    Sun: {2:2},{3:2}    Starting Player: {1:2}    Players: {4:2}    Your Points: {5:2}".format(state[83,0],state[84,0],state[85,0],state[86,0],state[87,0],state[88,0],state[89,0]))
                print("Bank:    Seeds: {0:2}    Small: {1:2}    Medium: {2:2}    Large: {3:2}    Light: {4:2}".format(state[78,0],state[79,0],state[80,0],state[81,0],state[82,0]))
                print("Store:   Seeds: {0:2}    Small: {1:2}    Medium: {2:2}    Large: {3:2}".format(state[74,0],state[75,0],state[76,0],state[77,0]))
                action_string = "Actions Avaliable:    "
                if np.isfinite(actions[0,0]):
                    action_string += "Pass,    "
                action_string += "Grow:"
                for i in range(37):
                    if np.isfinite(actions[i+1,0]):
                        action_string += "{},".format(i+1)
                action_string += "    Buy: "
                if np.isfinite(actions[38,0]):
                    action_string += "Seed, "
                if np.isfinite(actions[39,0]):
                    action_string += "Small Tree, "
                if np.isfinite(actions[40,0]):
                    action_string += "Medium Tree, "
                if np.isfinite(actions[41,0]):
                    action_string += "Large Tree, "
                print(action_string)
                print("-------------------------------------------")
                print("Action Key:    0=pass    1-37=Grow Tile x    38=Buy Seed    39=Buy Small Tree    40=Buy Medium Tree    41=Buy Large Tree")
                choosen_action_string = input("What action do you choose: ")
                choosen_action = -1
                if choosen_action_string.isdigit():
                    choosen_action=int(choosen_action_string)
                    if 0<=choosen_action and choosen_action<=len(actions) and np.isfinite(actions[choosen_action]):
                        valid_choice = True
                        break

                print("\n\n")
                print("INVALID ACTION")
                print("\n\n")

        return choosen_action
