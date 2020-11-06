import numpy as np

class initilize:
    number_of_states_to_save = 24
    # saved_states
    saved_states_count = 0
    # Theta

    def __init__(self,theta = None,hyper_parameters = None):
        self.D = []


    def phi(self,s):

    def prepare_to_learn(self,z_0):
        self.saved_states = np.tile(z_0,(number_of_states_to_save,1))
