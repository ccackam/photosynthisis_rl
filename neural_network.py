import numpy as np

class initilize:
    number_of_states_to_save = 24
    # saved_states
    saved_states_count = 0
    # Theta
    # A
    # Z

    def __init__(self,hyper_parameters = None,theta = None):
        # np.random.seed(10)
        if theta == None:
            self.hyper_parameters = hyper_parameters.copy()
            self.hyper_parameters["L"] = len(self.hyper_parameters["size"])-1
            self.theta = {}
            self.Z = {}
            self.A = {0:np.zeros((self.hyper_parameters["size"][0],self.hyper_parameters["m"]))}
            self.dL_dA = {}
            self.dL_dZ = {}
            self.dL_dw = {}
            self.dL_db = {}
            for i,(l,n) in enumerate(sorted(self.hyper_parameters["size"].items())[1:]):
                self.theta[l] = {"w":np.random.randn(n,self.hyper_parameters["size"][l-1])*0.01,"b":np.zeros((n,1))}
                self.Z[l] = np.zeros((n,self.hyper_parameters["m"]))
                self.A[l] = np.zeros((n,self.hyper_parameters["m"]))
                self.dL_dA[l] = np.zeros((n,self.hyper_parameters["m"]))
                self.dL_dZ[l] = np.zeros((n,self.hyper_parameters["m"]))
                self.dL_dw[l] = np.zeros((n,self.hyper_parameters["size"][l-1]))
                self.dL_db[l] = np.zeros((n,1))


    def forward_prop(self,x):
        if np.size(np.shape(x))>=2:
            self.hyper_parameters["m"] = x.shape[1]
        else:
            self.hyper_parameters["m"] = 1
        self.A[0] = np.reshape(x,(self.hyper_parameters["size"][0],self.hyper_parameters["m"]));
        for i,(l,n) in enumerate(sorted(self.hyper_parameters["size"].items())[1:]): # Fix ordering
            self.Z[l] = self.theta[l]["w"]@self.A[l-1] + self.theta[l]["b"]
            self.A[l] = self.activation(self.Z[l],self.hyper_parameters["activation"][l])
        # add drop out ability
        return np.squeeze(self.A[self.hyper_parameters["L"]])

    def backward_prop(self,dL_dyhat):
        self.dL_dA[self.hyper_parameters["L"]] = dL_dyhat
        for i,(l,n) in enumerate(sorted(self.hyper_parameters["size"].items(),reverse=True)[:-1]):
            self.dL_dZ[l] = self.dL_dA[l]*self.dA_dZ(self.Z[l],self.A[l],self.hyper_parameters["activation"][l])
            self.dL_dw[l] = self.dL_dZ[l]@self.A[l-1].T/self.hyper_parameters["m"]
            self.dL_db[l] = np.sum(self.dL_dZ[l],axis=1,keepdims=True)/self.hyper_parameters["m"]
            self.dL_dA[l-1] = self.theta[l]["w"].T@self.dL_dZ[l] # n[l-1]xm = n[l]xn[l-1] * n[l]xm

            self.theta[l]["w"] -= self.hyper_parameters["alpha"]*self.dL_dw[l]
            self.theta[l]["b"] -= self.hyper_parameters["alpha"]*self.dL_db[l]

    @staticmethod
    def activation(Z,type = "linear"):
        if type == "linear":
            A = Z
        elif type == "sigmoid":
            A = 1/(1+np.exp(-Z))
        elif type == "tanh":
            A = (np.exp(Z)-np.exp(-Z))/(np.exp(Z)+np.exp(-Z))
        elif type == "ReLU":
            A = np.maximum(0*Z,Z)
        elif type == "Leaky ReLU":
            A = np.maximum(0.01*Z,Z)
        elif type == "Softmax":
            A = np.exp(Z)/np.sum(np.exp(Z))
        return A

    @staticmethod
    def dA_dZ(Z = None,A = None,type = "linear"):
        if type == "linear":
            dA_dZ = np.ones(Z.shape)
        elif type == "sigmoid":
            dA_dZ = A*(1-A)
        elif type == "tanh":
            dA_dZ = 1-A**2
        elif type == "ReLU":
            dA_dZ = Z>=0
        elif type == "Leaky ReLU":
            dA_dZ = (Z>=0) + 0.01*(Z<0)
        elif type == "Softmax":
            dA_dZ = A*(1-A)
        return dA_dZ



# -- Cache
# if self.hyper_parameters["dropout"][layer-1] and d == None:
#     d = np.random.randn(Z.shape[0],Z.shape[1])>self.hyper_parameters["dropout"][layer-1]
#     Z *= d/(1-self.hyper_parameters["dropout"][layer-1])
# elif d != None:
#     Z *= d*len(d)/np.sum(d)
