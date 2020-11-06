import numpy as np
from  matplotlib import pyplot as plt
import time

class start:

    # Parameters
    board_side_length = 4
    # board_spots
    # board_spots_ranges
    # board
    """
    - board
        - spots
            - sun (bool)
            - handle (handle)
            - contains
                - handle (handle)
                - type (0-4) 0:None,1:Seed,2:Small Tree,3:Medium Tree,4:Large Tree
                - owner (int) -1:None otherwise Player ID
            - avaliable (bool)
            - planter (set)
            - planted (set)
        - fig (handle)
        - ax (handle)
    """

    # animate
    # player_count
    # players
    """
    - players
        - ID (int)
            - store
                - seeds
                - small
                - medium
                - large
            - bank
                - light
                - seeds
                - small
                - medium
                - large
            - points
            - init_turns
    """
    # turns_remaining
    # actions
    # initial_setup
    # initial_direction
    # players_turn
    # starting_player
    resource_names = ["seeds","small","medium","large"]
    resource_cost = {"seeds":[1,1,2,2,float("inf")],"small":[2,2,3,3,float("inf")],"medium":[3,3,4,float("inf")],"large":[4,5,float("inf")]}
    suns = [(1,0),(1,-2),(-1,-2),(-1,0),(-1,2),(1,2)]
    # sun_cycle
    ring_cycle_points = {1:[14,14,13,13,13,12,12,12,12],2:[17,16,16,14,14,13,13],3:[19,18,18,17,17],4:[22,21,20]}
    player_colors = [[1,0,0],[0,1,0],[0,0,1],[1,1,0]]
    # turn_index
    # time_in = [0,0,0,0,0,0,0]


    def __init__(self,animate):
        self.center = (0,0)
        board_spots_count = 0
        for i in range(self.board_side_length):
            board_spots_count += 2**(self.board_side_length!=(i+1))*(self.board_side_length+i)
        self.board_spots = []
        for i in range(self.board_side_length):
            for j in range(2*self.board_side_length-1-i):
                self.board_spots.append((i+j*2 - 2*(self.board_side_length-1),i*2))
                if(i):
                    self.board_spots.append((i+j*2 - 2*(self.board_side_length-1),-i*2))
        self.board = {"spots":{}}
        self.board_spots_ranges = {}
        for spot in self.board_spots:
            self.board["spots"][spot] = {"sun":True,"avaliable":True,"planter":set(),"planted":set(),"contains":{"type":0,"owner":-1}}
            self.board_spots_ranges[spot] = {1:set(),2:set(),3:set()}
            for site in self.board_spots:
                level = self.get_level(site,spot)
                if 0 < level and level < 4:
                    self.board_spots_ranges[spot][level].add(site)
        # np.random.seed(1)
        self.animate = animate

    def calculate_light(self):
        for spot in self.board_spots:
            self.board["spots"][spot]["sun"] = True
            if self.animate:
                self.board["spots"][spot]["handle"].set_facecolor((1,1,1))
        for spot in self.board_spots: # New light Points
            tree_here = self.board["spots"][spot]["contains"]["type"]
            if tree_here>1:
                for shade_distance in range(1,tree_here):
                    shaded_spot = (spot[0]+self.sun[0]*shade_distance , spot[1]+self.sun[1]*shade_distance)
                    if shaded_spot in self.board_spots:
                        self.board["spots"][shaded_spot]["sun"] = False
                        if self.animate:
                            self.board["spots"][shaded_spot]["handle"].set_facecolor((0.7,0.7,0.7))
                    else:
                        break
                # to_other_spot = self.board_spots-np.asarray(spot)
                # to_other_spot_length = np.sqrt(np.sum(to_other_spot*to_other_spot,axis = 1,keepdims=True))
                # with np.errstate(divide='ignore',invalid='ignore'):
                #     projected_to_other_spot = (to_other_spot@(self.sun[...,np.newaxis]))/to_other_spot_length
                # shade_distance = (self.board["spots"][spot]["contains"]["type"]-1)*2+1
                # for i,sun_allignment_factor in enumerate(projected_to_other_spot):
                #     other_spot = self.board_spots[i]
                #     if (sun_allignment_factor==1) and (to_other_spot_length[i])<=shade_distance and self.board["spots"][other_spot]["contains"]["type"]<=self.board["spots"][spot]["contains"]["type"]:
                #         self.board["spots"][other_spot]["sun"] = False
                #         if self.animate:
                #             self.board["spots"][other_spot]["handle"].set_facecolor((0.7,0.7,0.7))
        for spot in self.board_spots:
            self.board["spots"][spot]["avaliable"] = True
            if self.board["spots"][spot]["contains"]["type"] and self.board["spots"][spot]["sun"]:
                self.players[self.board["spots"][spot]["contains"]["owner"]]["bank"]["light"] += (self.board["spots"][spot]["contains"]["type"]-1)
                if self.players[self.board["spots"][spot]["contains"]["owner"]]["bank"]["light"]>20:
                    self.players[self.board["spots"][spot]["contains"]["owner"]]["bank"]["light"]=20

    def take_action(self,action_index):
        final_score = None
        if action_index == 0: # Pass Turn
            self.players_turn = (self.players_turn + 1) % self.player_count
            for spot in self.board_spots:
                self.board["spots"][spot]["planter"] = set()
                self.board["spots"][spot]["planted"] = set()
            if self.players_turn == self.starting_player: # Time to Rotate Sun
                self.turns_remaining -= 1
                if self.turns_remaining == 0: # Game End
                    final_score = []
                    for i in range(self.player_count):
                        light_points = np.squeeze(np.maximum(0,np.floor((self.players[i]["bank"]["light"]+1)/3-1)))
                        self.players[i]["points"] += light_points
                        final_score.append(self.players[i]["points"])
                    game_over_string = "GAME OVER - Final Score:    "
                    for i in range(len(final_score)):
                        game_over_string += str(i) + ": " + str(final_score[i]) + "    "
                    print(game_over_string)
                self.starting_player = (self.starting_player+1) % self.player_count
                self.players_turn = self.starting_player
                self.sun_cycle = (self.sun_cycle+1) % 6
                self.sun = self.suns[self.sun_cycle]
                if self.animate:
                    length_of_sun = np.sqrt(self.sun[0]**2+self.sun[1]**2)
                    self.board["sun"].set_UVC(self.sun[0]/length_of_sun,self.sun[1]/length_of_sun)
                self.calculate_light()
        elif 1 <= action_index and action_index <= 37: # Grow
            if self.initial_setup: # Intial Setup
                spot = self.board_spots[action_index-1]
                self.board["spots"][spot]["contains"]["owner"] = self.players_turn
                self.board["spots"][spot]["contains"]["type"] = 2
                self.players[self.players_turn]["bank"]["small"] -= 1
                if self.animate:
                    self.board["spots"][spot]["contains"]["handle"].set_facecolor(self.player_colors[self.players_turn])
                self.players[self.players_turn]["init_turns"] -= 1
                self.players_turn = (self.players_turn + self.initial_direction) % self.player_count
                if self.initial_direction == 1 and self.players[self.players_turn]["init_turns"] == 1:
                    self.initial_direction = -1
                    self.players_turn = (self.players_turn + self.initial_direction) % self.player_count
                elif self.initial_direction == -1 and self.players[self.players_turn]["init_turns"] == 0:
                    self.initial_direction = 1
                    self.players_turn = (self.players_turn + self.initial_direction) % self.player_count
                    self.initial_setup = False
                    self.calculate_light()
            else: # Normal Gameplay
                self.players[self.players_turn]["bank"]["light"] -= self.actions[action_index]
                spot = self.board_spots[action_index-1]
                self.board["spots"][spot]["avaliable"] = False
                if self.board["spots"][spot]["contains"]["type"] == 0: # Seed
                    self.board["spots"][spot]["contains"]["owner"] = self.players_turn
                    self.board["spots"][spot]["contains"]["type"] += 1
                    self.players[self.players_turn]["bank"]["seeds"] -= 1
                    for possible_planter in self.board["spots"][spot]["planter"]:
                        self.board["spots"][possible_planter]["planted"].add(spot)
                        if len(self.board["spots"][spot]["planter"]) == 1:
                            self.board["spots"][possible_planter]["avaliable"] = False
                    if self.animate:
                        self.board["spots"][spot]["contains"]["handle"].set_facecolor(self.player_colors[self.players_turn])
                elif self.board["spots"][spot]["contains"]["type"] >= 4: # Life Cycle
                    self.board["spots"][spot]["contains"]["owner"] = -1
                    if self.animate:
                        self.board["spots"][spot]["contains"]["handle"].set_facecolor([0,0,0])
                    self.board["spots"][spot]["contains"]["type"] = 0
                    self.board["spots"][spot]["planted"] = set()
                    self.board["spots"][spot]["planter"] = set()
                    self.board["spots"][spot]["avaliable"] = True
                    if spot == self.center:
                        level = 4
                    else:
                        for i in range(1,4):
                            if spot in self.board_spots_ranges[self.center][i]:
                                level = 4-i
                    for i in range(5):
                        if level==i:
                            points_won = 0
                            break
                        if self.ring_cycle_points[level-i]:
                            points_won = self.ring_cycle_points[level-i].pop(0)
                            break
                    self.players[self.players_turn]["points"] += points_won
                    if self.players[self.players_turn]["store"]["large"] < 2:
                        self.players[self.players_turn]["store"]["large"] += 1
                else: # all others
                    if self.players[self.players_turn]["store"][self.resource_names[self.board["spots"][spot]["contains"]["type"]-1]] < (len(self.resource_cost[self.resource_names[self.board["spots"][spot]["contains"]["type"]-1]])-1):
                        self.players[self.players_turn]["store"][self.resource_names[self.board["spots"][spot]["contains"]["type"]-1]] += 1
                    self.board["spots"][spot]["contains"]["type"] += 1
                    self.players[self.players_turn]["bank"][self.resource_names[self.board["spots"][spot]["contains"]["type"]-1]] -= 1
            for planted_spot in self.board["spots"][spot]["planted"]:
                self.board["spots"][planted_spot]["planter"].remove(spot)
                if len(self.board["spots"][planted_spot]["planter"]) == 1:
                    for other_possible_planter in self.board["spots"][planted_spot]["planter"]:
                        self.board["spots"][other_possible_planter]["avaliable"] = False
                    break
                else:
                    for other_possible_planter in self.board["spots"][planted_spot]["planter"]:
                        for other_other_possible_planter in self.board["spots"][planted_spot]["planter"]:
                            if (other_possible_planter != other_other_possible_planter) and self.board["spots"][other_possible_planter]["planted"] == self.board["spots"][other_other_possible_planter]["planted"]:
                                self.board["spots"][other_possible_planter]["avaliable"] = False
                                self.board["spots"][other_other_possible_planter]["avaliable"] = False


            if self.animate:
                self.board["spots"][spot]["contains"]["handle"].set_radius(self.board["spots"][spot]["contains"]["type"]/5)

        elif 38 <= action_index:
            self.players[self.players_turn]["bank"]["light"] -= self.actions[action_index]
            self.players[self.players_turn]["bank"][self.resource_names[action_index-38]] += 1
            self.players[self.players_turn]["store"][self.resource_names[action_index-38]] -= 1
        return final_score

    def get_state(self):
        """
        State Vector Definition:
        [Spot Size[0:36],Spot Owner[0:36],store[0:3],bank[0:4],turns remaining,starting player,sun[0:1],players,points]
        """
        state = np.zeros((90,1))

        index = 0
        for spot in self.board_spots:
            state[index,0] = self.board["spots"][spot]["contains"]["type"]
            state[index+37,0] = self.board["spots"][spot]["contains"]["owner"]
            index += 1
        index += 37
        for resource in self.resource_names:
            state[index] = self.players[self.players_turn]["store"][resource]
            state[index+4] = self.players[self.players_turn]["bank"][resource]
            index += 1
        index += 4
        state[index] = self.players[self.players_turn]["bank"]["light"]
        index += 1
        state[index] = self.turns_remaining
        index += 1
        state[index] = self.starting_player
        index += 1
        state[index] = self.sun[0]
        index += 1
        state[index] = self.sun[1]
        index += 1
        state[index] = self.player_count
        index += 1
        state[index] = self.players[self.players_turn]["points"]
        index += 1
        state[index] = self.initial_setup
        return state

    def get_actions(self):
        """
        Action Vector Definition:
        [pass,grow[0:36],buy[0:3]]
        """
        self.actions = np.zeros((42,1)) + float('inf')
        index = 0

        # Pass Action is always avaliable
        self.actions[index,0] = 0
        index += 1

        if self.players[self.players_turn]["bank"]["light"] and not self.initial_setup: # Is Grow Avaliable
            for spot in self.board_spots:
                if self.board["spots"][spot]["contains"]["owner"]==self.players_turn and self.board["spots"][spot]["avaliable"]:
                    if   (self.board["spots"][spot]["contains"]["type"] == 1) and self.players[self.players_turn]["bank"]["small"]  and (self.players[self.players_turn]["bank"]["light"]>=1):
                        self.actions[index,0] = 1
                    elif (self.board["spots"][spot]["contains"]["type"] == 2):
                        if self.players[self.players_turn]["bank"]["medium"] and (self.players[self.players_turn]["bank"]["light"]>=2):
                            self.actions[index,0] = 2
                        if self.players[self.players_turn]["bank"]["seeds"] and (self.players[self.players_turn]["bank"]["light"]>=1):
                            self.set_plant_radius(spot,1)
                    elif (self.board["spots"][spot]["contains"]["type"] == 3):
                        if self.players[self.players_turn]["bank"]["large"] and (self.players[self.players_turn]["bank"]["light"]>=3):
                            self.actions[index,0] = 3
                        if self.players[self.players_turn]["bank"]["seeds"] and (self.players[self.players_turn]["bank"]["light"]>=1):
                            self.set_plant_radius(spot,2)
                    elif (self.board["spots"][spot]["contains"]["type"] == 4):
                        if (self.players[self.players_turn]["bank"]["light"]>=4):
                            self.actions[index,0] = 4
                        if self.players[self.players_turn]["bank"]["seeds"] and (self.players[self.players_turn]["bank"]["light"]>=1):
                            self.set_plant_radius(spot,3)
                index += 1
            for resource in self.resource_names: # Is Buy Avaliable
                purchase_cost = self.resource_cost[resource][(len(self.resource_cost[resource])-1)-(self.players[self.players_turn]["store"][resource])]
                if  self.players[self.players_turn]["store"][resource] and (purchase_cost <= self.players[self.players_turn]["bank"]["light"]):
                    self.actions[index,0] = purchase_cost
                index += 1
        elif self.initial_setup: # Ininitial Setup you get free actions in any space
            self.actions[0,0] = float("inf")
            for spot in self.board_spots_ranges[self.center][3]:
                if not self.board["spots"][spot]["contains"]["type"]:
                    self.actions[index,0] = 2
                index += 1
        return self.actions

    def set_plant_radius(self,spot,radius):
        for level in range(1,radius+1):
            for site in self.board_spots_ranges[spot][level]:
                if not self.board["spots"][site]["contains"]["type"]:
                    self.actions[self.board_spots.index(site)+1] = 1
                    self.board["spots"][site]["planter"].add(spot)

    def new_game(self,player_count):
        self.initial_setup = True
        self.initial_direction = 1
        # Create Players
        self.player_count = player_count
        self.players = {"init_turns":2}
        for i in range(self.player_count):
            self.players[i] = {"store":{"seeds":4,"small":4,"medium":3,"large":2},"bank":{"light":0,"seeds":2,"small":4,"medium":1,"large":0},"points":0,"init_turns":2}
        if self.player_count == 2:
            self.turns_remaining = 18
        else:
            self.turns_remaining = 24
        self.players_turn = 0
        self.turn_index = 0
        self.starting_player = 0
        self.sun_cycle = 0

        # Create Playing Board
        for spot in self.board_spots:
            self.board["spots"][spot]["sun"] = True
            self.board["spots"][spot]["avaliable"] = True
            self.board["spots"][spot]["planter"] = set()
            self.board["spots"][spot]["planted"] = set()
            self.board["spots"][spot]["contains"]["type"] = 0
            self.board["spots"][spot]["contains"]["owner"] = -1
        self.sun = self.suns[self.sun_cycle]
        self.ring_cycle_points = {1:[14,14,13,13,13,12,12,12,12],2:[17,16,16,14,14,13,13],3:[19,18,18,17,17],4:[22,21,20]}
        if self.animate:
            self.initalize_animation()

    def get_level(self,spot,center):
        x,y = spot
        cx,cy = center
        for i in range(4):
            t = (2*i+1)
            l = cx - t
            r = cx + t
            if y<2*x-2*l+cy and y<t+cy and y<-2*x+2*r+cy and y>-2*x+2*l+cy and y>-t+cy and y>2*x-2*r+cy:
                return i
        return -1

    def initalize_animation(self):

        # Draw Playing board
        self.board["fig"], self.board["ax"] = plt.subplots()
        plt.ion()
        plt.show()

        cx,cy = self.center

        self.board["ax"].set_facecolor([0,1,0])

        index = 1
        for spot in self.board_spots:
            self.board["spots"][spot]["handle"] = plt.Circle(spot, 1, facecolor=(1,1,1), edgecolor=[0,0,0])
            self.board["ax"].add_artist(self.board["spots"][spot]["handle"])
            self.board["spots"][spot]["contains"]["handle"] = plt.Circle(spot, 0/10, facecolor=(0,0,0), edgecolor=[0,0,0])
            self.board["ax"].add_artist(self.board["spots"][spot]["contains"]["handle"])
            plt.text(spot[0]-0.25,spot[1]-0.25,str(index))
            index += 1

        self.board["sun"] = plt.quiver(cx-(self.board_side_length-1)*2,cy+(self.board_side_length-1)*2,self.sun[0],self.sun[1],facecolor=[1,1,0],edgecolor=[0,0,0])

        width = 4*self.board_side_length
        self.board["ax"].set_ylim([cy-width/2,cy+width/2])
        self.board["ax"].set_xlim([cy-width/2,cy+width/2])
        self.redraw()

    def redraw(self):
        plt.draw()
        plt.pause(0.001)
