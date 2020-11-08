import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
from  matplotlib import pyplot as plt
import random

class PhotosynthisisEnv(gym.Env):
# class PhotosynthisisEnv:
    metadata = {'render.modes': ['human']}
    """
    - board
        - spots (tuple)
            - sun (bool)
            - spot handle (handle)
            - tree handle (handle)
            - type (0-4) 0:None,1:Seed,2:Small Tree,3:Medium Tree,4:Large Tree
            - owner (int) -1:None otherwise Player ID
            - avaliable (bool)
            - planter (set)
            - level
        - fig (handle)
        - ax (handle)
    """
    """
    - players
        - ID (int)
            - store
                - seeds
                - small
                - medium
                - large
            - bank
                - seeds
                - small
                - medium
                - large
            - light
            - points
            - init_turns
    """
    empty = None
    seed = 0
    small = 1
    medium = 2
    large = 3
    random = 0
    logic = 1
    old_ai = 2
    human = 3
    ai = 4
    grow_costs = {None:1,0:1,1:2,2:3,3:4}
    store_spots = {0:[1,1,2,2],1:[2,2,3,3],2:[3,3,4],3:[4,5]}
    suns = [(2,0),(1,-2),(-1,-2),(-2,0),(-1,2),(1,2)]
    initial_ring_cycle_points = {1:[14,14,13,13,13,12,12,12,12],2:[17,16,16,14,14,13,13],3:[19,18,18,17,17],4:[22,21,20]}
    player_colors = [[1,0,0],[0,1,0],[0,0,1],[1,1,0]]
    center = (0,0)
    drawing_initialized = False
    random_players = True
    allowed_player_types = [0,1]
    prespecified_players = [4,None,None,None]
    action_space = spaces.Discrete(42)
    observation_space = spaces.Box(low=0,high=1,shape=(88,),dtype=np.float16)
    record = [0,0,0]


    def __init__(self):
        # Initialize Enviroment
        random.seed(10)
        self.__create_board()
        self.reset()

    def step(self, ai_action_index, fresh_ai_action_avaliable=True,manually_created=False):
        while not self.done:
            self.__get_actions()
            self.__get_state()
            self.__get_reward()

            if np.count_nonzero(np.isfinite(self.actions)) == 1:
                action_index = 0
            else:
                if self.players[self.players_turn]["type"] == self.random:
                    action_index = self.__act_randomly()
                elif self.players[self.players_turn]["type"] == self.logic:
                    action_index = self.__act_logically()
                elif self.players[self.players_turn]["type"] == self.old_ai:
                    pass # TODO
                elif self.players[self.players_turn]["type"] == self.human:
                    action_index = self.__act_humanly()
                elif self.players[self.players_turn]["type"]== self.ai:
                    if fresh_ai_action_avaliable:
                        action_index = ai_action_index
                        fresh_ai_action_avaliable = False
                    else:
                        return self.state, self.reward, self.done, {}

            self.__take_turn(action_index)

            if manually_created:
                self.render()

        self.__get_state()
        self.__get_reward()
        return self.state, self.reward, self.done, {}

    def reset(self):
        # TODO take in agents directly here

        # Reset game variables
        self.initial_setup = True
        self.initial_direction = 1
        self.turns_remaining = 18
        self.turn_index = 0
        self.sun_cycle = 0
        self.sun = self.suns[0]
        self.ring_cycle_points = self.initial_ring_cycle_points
        self.done = False
        self.possible_actions = []
        self.reward = 0

        # Rest player variables
        self.players = {}
        if self.random_players:
            number_of_required_players = np.sum(x is not None for x in self.prespecified_players)

            min_number_of_players = np.maximum(number_of_required_players,2)
            self.player_count = random.randint(min_number_of_players,4)

            visitors = random.choices(self.allowed_player_types,k=(self.player_count-number_of_required_players))

            self.prespecified_players = [x for x in self.prespecified_players if (not x == None)]+visitors
            random.shuffle(self.prespecified_players)
        else:
            self.player_count = len(self.prespecified_players)
        for i,type in enumerate(self.prespecified_players):
            self.players[i] = {"store":{self.seed:4,self.small:4,self.medium:3,self.large:2},"bank":{self.seed:2,self.small:4,self.medium:1,self.large:0},"light":0,"points":0,"init_turns":2,"type":type}
        self.players_turn = random.randrange(0,self.player_count)
        self.starting_player = self.players_turn

        # Reset board variables
        for spot in self.board_spots:
            self.board[spot]["sun"] = True
            self.board[spot]["avaliable"] = True
            self.board[spot]["planter"] = set()
            self.board[spot]["type"] = self.empty
            self.board[spot]["owner"] = None

        self.__get_actions()
        self.__get_state()
        self.__get_reward()

        return self.state

    def render(self, mode='human', close=False):
        if mode == 'human':

            if not self.drawing_initialized:
                self.__initalize_animation()

            # Update the Sun
            length_of_sun = np.sqrt(self.sun[0]**2+self.sun[1]**2)
            self.board["sun"].set_UVC(self.sun[0]/length_of_sun,self.sun[1]/length_of_sun)

            # Draw the Board
            for spot in self.board_spots:
                if not (self.board[spot]["type"] == self.empty):
                    self.board[spot]["tree handle"].set_radius((self.board[spot]["type"]+1)/5)
                    self.board[spot]["tree handle"].set_facecolor(self.player_colors[self.board[spot]["owner"]])
                else:
                    self.board[spot]["tree handle"].set_radius(0)

                if self.board[spot]["sun"]:
                    self.board[spot]["spot handle"].set_facecolor((1,1,1))
                else:
                    self.board[spot]["spot handle"].set_facecolor((0.7,0.7,0.7))

            plt.draw()
            plt.pause(0.001)

            if self.done:
                game_over_string = "GAME OVER - Final Score:    "
                for player in range(self.player_count):
                    game_over_string += str(player) + ": " + str(self.players[player]["points"]) + "    "
                print(game_over_string)

    def __take_turn(self, action_index):
        # Confirm that this player can aford this action
        if self.actions[action_index] <= self.players[self.players_turn]["light"]:

            # input("Press Enter to Advance: ")
            # print(self.actions)
            # print(action_index)

            # Pay cost of the action
            self.players[self.players_turn]["light"] -= self.actions[action_index]

            # Take indicated Action
            if action_index == 0: # Pass Turn
                self.__on_pass()
            elif 1 <= action_index and action_index <= 37: # Grow
                spot = self.board_spots[action_index - 1]
                self.__on_grow(spot)
            elif 38 <= action_index: # Buy
                type = action_index - 38
                self.__on_buy(type)

            # We must keep track of which tree planted which seed.
            self.__update_seeds()

    def __calculate_light(self):
        # Reset the map
        for spot in self.board_spots:
            self.board[spot]["sun"] = True

        # Find the shadow for each tree
        for spot in self.board_spots:
            # Variable for readability
            tree_here = self.board[spot]["type"]

            # If this tree casts a shadow
            if (not tree_here == None) and (not tree_here == self.seed):
                # For the range of the shade
                for shade_distance in range(1,tree_here+1):
                    # Calculate the shaded spot
                    shaded_spot = (spot[0]+self.sun[0]*shade_distance , spot[1]+self.sun[1]*shade_distance)

                    # If this spot is on the board
                    if (shaded_spot in self.board_spots) and ((self.board[shaded_spot]["type"] == self.empty) or (self.board[shaded_spot]["type"] <= self.board[spot]["type"])):
                        # Mark it as shaded
                        self.board[shaded_spot]["sun"] = False
                    else: # There is no point in continuing if the previous spot was beyond the board becasue the board is convex
                        break

        # Find the spots that have light shining on them
        for spot in self.board_spots:
            if self.board[spot]["type"] and self.board[spot]["sun"]:
                # Add light points.
                self.players[self.board[spot]["owner"]]["light"] += self.board[spot]["type"]

                # Saturate at a maximum of 20 points.
                if self.players[self.board[spot]["owner"]]["light"]>20:
                    self.players[self.board[spot]["owner"]]["light"]=20

    def __get_state(self):
        """
        State Vector Definition:
        [Spot Size[0:36],Spot Owner[0:36],store[0:3],bank[0:3],light,turns remaining,starting player,sun,players,initial_setup]
        """
        self.state = np.zeros((88,))

        # Get the current value and normalize by the maximum value
        for i,spot in enumerate(self.board_spots):
            self.state[i] = (self.board[spot]["type"]+1)/4 if not self.board[spot]["type"] == None else 0
            self.state[i+37] = (self.board[spot]["owner"]+1)/4 if not self.board[spot]["owner"] == None else 0

        for resource in range(self.large+1):
            self.state[74+resource] = self.players[self.players_turn]["store"][resource]/4
            self.state[74+resource+4] = self.players[self.players_turn]["bank"][resource]/8

        self.state[82] = self.players[self.players_turn]["light"]/20
        self.state[83] = self.turns_remaining/18
        self.state[84] = self.starting_player/3
        self.state[85] = self.sun_cycle/5
        self.state[86] = self.player_count/4
        self.state[87] = self.initial_setup

    def __get_actions(self):
        """
        Action Vector Definition:
        [pass,grow[0:36],buy[0:3]]
        """

        # Initialize with inifite cost to do anything
        self.actions = np.zeros((42)) + float("Inf")
        index = 0

        # Pass Action is always avaliable
        self.actions[index] = 0
        index += 1

        # Possible Actions
        if self.initial_setup: # Initial Setup you get free actions in any space

            # Pass is not avaliable in this case
            self.actions[0] = float("Inf")

            # Must build initially along the outer ring (3 away from center)
            for spot in self.board[self.center]["ranges"][3]:
                # If someone hasn't already built there
                if self.board[spot]["type"]==self.empty:
                    self.actions[self.board_spots.index(spot)+1] = 0

        # When not in the initial setup actions cost money
        elif self.players[self.players_turn]["light"]: # Normal game

            # For readability
            spending_cash = self.players[self.players_turn]["light"]

            # Grow Actions
            for spot in self.board_spots:
                # Check who owns this spot and confirm that this spot hasn't had an action used on it before
                # TODO need to check if initial placement is on edge also need to confirm seed locaitons are allowed
                if self.board[spot]["owner"]==self.players_turn and self.board[spot]["avaliable"]:

                    # Variables for readability
                    type = self.board[spot]["type"]
                    next_type = self.board[spot]["type"]+1 if not type == self.large else None
                    cost = self.grow_costs[type]

                    # Determine cost to grow here
                    self.actions[self.board_spots.index(spot)+1] = cost if (cost <= spending_cash and (next_type == None or self.players[self.players_turn]["bank"][next_type])) else float("Inf") # TODO change bank and store keys to numbers

                    # Determin where this tree can plant seeds
                    if (not self.board[spot]["type"] == self.seed) and self.grow_costs[self.seed] <= spending_cash and self.players[self.players_turn]["bank"][self.seed]:
                        self.__set_plant_radius(spot,type)

            # Buy Actions
            for resource in range(self.large+1):

                # Variables for readability:
                store_spots = len(self.store_spots[resource])
                inventory = self.players[self.players_turn]["store"][resource]
                purchase_cost = self.store_spots[resource][store_spots - inventory - 1]
                spending_cash = self.players[self.players_turn]["light"]

                # The price is finite if inventory is avaliable,
                self.actions[38+resource] = self.store_spots[resource][store_spots-inventory] if (inventory and (purchase_cost <= spending_cash)) else float("Inf")

        # Get possible actions for quick easy referance
        self.possible_actions = [i for i,a in enumerate(self.actions) if a <= self.players[self.players_turn]["light"]]

    def __get_level(self,spot,center):
        # Returns the distance in board hexes between two spots.
        x,y = spot
        cx,cy = center

        # A spot is ignored if it is more then 4 spots away.
        for i in range(4):
            # Find the center point of the next hex
            t = (2*i+1)
            l = cx - t
            r = cx + t

            # Determine if that center point is outside a large hex drawn around the current level-1.
            if y<2*x-2*l+cy and y<t+cy and y<-2*x+2*r+cy and y>-2*x+2*l+cy and y>-t+cy and y>2*x-2*r+cy:
                return i
        return -1 # Some error occured.

    def __initalize_animation(self):
        # Draw Playing board

        # Initialize the figure
        self.board["fig"], self.board["ax"] = plt.subplots()
        plt.ion()
        plt.show()

        # Center of the board.
        cx,cy = self.center

        # Background color
        self.board["ax"].set_facecolor([0,1,0])

        # Draw the hexes and save relivant drawing handles
        index = 1
        for spot in self.board_spots:
            # Actual spot
            self.board[spot]["spot handle"] = plt.Circle(spot, 1, facecolor=(1,1,1), edgecolor=[0,0,0])
            self.board["ax"].add_artist(self.board[spot]["spot handle"])

            # Tree in spot (this object is invisible when nothing is there)
            self.board[spot]["tree handle"] = plt.Circle(spot, 0/10, facecolor=(0,0,0), edgecolor=[0,0,0])
            self.board["ax"].add_artist(self.board[spot]["tree handle"])

            # Label each spot for ease of playing the game
            plt.text(spot[0]-0.25,spot[1]-0.25,str(index))

            # Advance the index
            index += 1

            self.drawing_initialized = True

        # Sun arrow
        self.board["sun"] = plt.quiver(cx-6,cy+6,self.sun[0],self.sun[1],facecolor=[1,1,0],edgecolor=[0,0,0])

        # Set the board limits so it is square
        width = 4*4
        self.board["ax"].set_ylim([cy-width/2,cy+width/2])
        self.board["ax"].set_xlim([cy-width/2,cy+width/2])

        self.render()

    def __create_board(self):
        # Create a ordered list to track the unordered dictionary we will use. This will be usefull for creating an action vector that is always in the same order.
        self.board_spots = []
        for i in range(4):
            for j in range(7-i):
                self.board_spots.append((i+j*2-6,i*2))
                if(i):
                    self.board_spots.append((i+j*2-6,-i*2))

        # Create the actual board
        self.board = {}
        for spot in self.board_spots:
            # Initialize the spot
            self.board[spot] = {"sun":True,"avaliable":True,"planter":set(),"contains":{"type":self.empty,"owner":None},"ranges":{1:set(),2:set(),3:set()},"level":-1}

        # Save for later use the distance between this spot and all othe spots.
        for spot in self.board_spots:
            for other_spot in self.board_spots:
                level = self.__get_level(other_spot,spot)
                if 0 < level and level < 4:
                    self.board[spot]["ranges"][level].add(other_spot)
                if spot == self.center: # If this is the center we will also save the level for convenience.
                    self.board[other_spot]["level"] = level

    def __update_seeds(self):
        # Find all of the seeds on the board that were just planted this turn
        seeds = set()
        for spot in self.board_spots:
            self.board[spot]["planter"] = set()
            if self.board[spot]["type"] == self.seed and not self.board[spot]["avaliable"]:
                seeds.add(spot)

        # Find all of the trees that could have planted those seeds
        for seed in seeds:
            for distance in range(1,4): # Must be in range
                for potential_planter in self.board[seed]["ranges"][distance]: # For each seed in that range
                    # If there is a valid tree in this spot and it is large enough to plant this seed
                    if  (self.board[potential_planter]["owner"] == self.board[seed]["owner"]) and (distance <= self.board[potential_planter]["type"]) and self.board[potential_planter]["avaliable"]:
                        # Save the potential planter
                        self.board[seed]["planter"].add(potential_planter)

        # If the number of poential planters is exactly equal to the number of seeds with the exact same list of potential planters
        # Then it doesn't mater which tree planted those seeds but we know those trees have all been used this turn and should not be avaliable.
        for seed1 in seeds:
            # Count the duplicates
            duplicate_count = 0
            for seed2 in seeds:
                if self.board[seed1]["planter"] == self.board[seed2]["planter"]:
                    duplicate_count += 1
            # If the above conditions are met then we must mark the trees as unavaliable.
            # print("---------")
            # print(seed1)
            # print(duplicate_count)
            # print(self.board[seed1]["planter"])
            if duplicate_count == len(self.board[seed1]["planter"]):
                for planter in self.board[seed1]["planter"]:
                    self.board[planter]["avaliable"] = False

    def __on_pass(self):
        # Advance to the next players turn
        self.players_turn = (self.players_turn + 1) % self.player_count

        # Rotate Sun
        if self.players_turn == self.starting_player:
            # Decrease the turns remaining counter
            self.turns_remaining -= 1

            # Check for end of game.
            if self.turns_remaining == 0:
                self.done = True
                for player in range(self.player_count): # Add light points
                    self.players[player]["points"] += np.squeeze(np.maximum(0,np.floor((self.players[player]["light"]+1)/3-1)))

            # Advance starting player
            self.starting_player = (self.starting_player+1) % self.player_count
            self.players_turn = self.starting_player

            # Advance sun
            self.sun_cycle = (self.sun_cycle+1) % 6
            self.sun = self.suns[self.sun_cycle]

            # Perform the photosynthisis phase
            self.__calculate_light()

            # Reset for next set of turns
            self.__reset_avaliability()

    def __on_grow(self,spot):
        if self.initial_setup:
            self.__initial_setup(spot)
        else:
            self.__normal_grow(spot)

    def __initial_setup(self,spot):

        # Plant a tree in the choosen spot
        self.board[spot]["owner"] = self.players_turn
        self.board[spot]["type"] = self.small
        self.players[self.players_turn]["bank"][self.small] -= 1

        # Advance to the next players turn
        self.players[self.players_turn]["init_turns"] -= 1
        self.players_turn = (self.players_turn + self.initial_direction) % self.player_count

        # Reverse direction if nessisary
        if self.initial_direction == 1 and self.players[self.players_turn]["init_turns"] == 1:
            self.initial_direction = -1
            self.players_turn = (self.players_turn + self.initial_direction) % self.player_count
        elif self.initial_direction == -1 and self.players[self.players_turn]["init_turns"] == 0:
            self.initial_direction = 1
            self.players_turn = (self.players_turn + self.initial_direction) % self.player_count
            self.initial_setup = False

            # Perform initial photosynthisis phase
            self.__calculate_light()

    def __normal_grow(self,spot):

        # The Action depends on the previous state of the spot
        previous_state = self.board[spot]["type"]
        new_state = previous_state+1 if ((not previous_state == self.empty) and (not previous_state == self.large)) else (self.seed if previous_state is self.empty else (self.empty if previous_state is self.large else _))

        # Update data accordingly
        self.board[spot]["owner"] = self.players_turn if not previous_state == self.large else None
        self.board[spot]["type"] = new_state
        self.board[spot]["avaliable"] = False if not previous_state == self.large else True

        # Return tree to store if space is avaliable
        if (not previous_state == self.empty) and (self.players[self.players_turn]["store"][previous_state] < len(self.store_spots[previous_state])):
            self.players[self.players_turn]["store"][previous_state] += 1

        if not previous_state == self.large:
            # Remove the new type from the bank
            self.players[self.players_turn]["bank"][new_state] -= 1
        else:
            # Collect points for life cycling
            self.__draw_points(spot)

    def __draw_points(self,spot):
        # Ensure that there are tiles left to be taken
        # Iterate through each lower level
        index = self.board[spot]["level"]
        points_won = 0
        while index>0:
            index -= 1
            # take the highest level with points avaliable
            if self.ring_cycle_points[self.board[spot]["level"]]:
                points_won = self.ring_cycle_points[self.board[spot]["level"]].pop(0)
                break

        # Add these points to the player's total
        self.players[self.players_turn]["points"] += points_won

    def __on_buy(self,item_bought):
        # Take item from store and put it in the bank.
        self.players[self.players_turn]["bank"][item_bought] += 1
        self.players[self.players_turn]["store"][item_bought] -= 1

    def __reset_avaliability(self):
        # Set the avaliability of all spots to true for the next sun station.
        for spot in self.board_spots:
            self.board[spot]["avaliable"] = True

    def __get_reward(self):
        if self.done:
            for k in self.players:
                if self.players[k]["type"] == self.ai:
                    rl_score = 0
                    other_scores = np.zeros(self.player_count-1)
                    index = 0
                    for k2 in self.players:
                        if not k2 == k:
                            other_scores[index] = self.players[k2]["points"]
                            index += 1
                        else:
                            rl_score = self.players[k2]["points"]
                    self.reward = rl_score-max(other_scores) # TODO handle tie
                    if self.reward > 0:
                        self.record[0] += 1
                    elif self.reward == 0:
                        self.record[1] += 1
                    else:
                        self.record[2] += 1
                    break
        else:
            self.reward = 0

    def __set_plant_radius(self,spot,radius):
        for level in range(1,radius+1):
            for site in self.board[spot]["ranges"][level]:
                if self.board[site]["type"] == self.empty:
                    self.actions[self.board_spots.index(site)+1] = 1

    def __act_randomly(self):
        return random.choice(self.possible_actions)

    def __act_logically(self):
        weights = np.zeros(len(self.possible_actions))

        for i,action in enumerate(self.possible_actions):
            if action == 0:
                weights[i] = 4/(self.players[self.players_turn]["light"]) if not (self.players[self.players_turn]["light"] == 0) else 1000
            elif 1 <= action and action <= 37:
                if self.turns_remaining <= 5:
                    if self.board[self.board_spots[action-1]]["owner"] == self.players_turn:
                        weights[i] = 1
                else:
                    weights[i] = 1
            elif 38 <= action and action <= 41:
                if self.turns_remaining > 5:
                    weights[i] = 1

        if sum(weights)==0:
            weights[0] = 1

        return random.choice(self.possible_actions)

    def __act_humanly(self):
        pass # TODO fix state
        # choosen_action = 0
        #
        # while 1:
        #     print(self.color + "'s Turn: ")
        #     print("Game Details:    Turns Remaining: {0:2}    Initial Setup: {5:2}    Sun: {2:2}    Starting Player: {1:2}    Players: {3:2}".format(self.turns_remaining,self.initial_setup,self.sun_cycle,self.starting_player,self.player_count))
        #     print("Bank:    Seeds: {0:2}    Small: {1:2}    Medium: {2:2}    Large: {3:2}    Light: {4:2}".format(self.players,self.state[77,0]*8,self.state[78,0]*8,self.state[79,0]*8,self.state[80,0]*20))
        #     print("Store:   Seeds: {0:2}    Small: {1:2}    Medium: {2:2}    Large: {3:2}".format(self.state[72,0]*4,self.state[73,0]*4,self.state[74,0]*4,self.state[75,0]*4))
        #     print("-------------------------------------------")
        #     print("Action Key:    0=pass    1-37=Grow Tile x    38=Buy Seed    39=Buy Small Tree    40=Buy Medium Tree    41=Buy Large Tree")
        #     choosen_action_string = input("What action do you choose: ")
        #     choosen_action = -1
        #     if choosen_action_string.isdigit():
        #         choosen_action=int(choosen_action_string)
        #         if 0<=choosen_action and choosen_action<len(self.actions):
        #             break
        #
        #     print("\n\n")
        #     print("INVALID ACTION")
        #     print("\n\n")
        #
        # return choosen_action
