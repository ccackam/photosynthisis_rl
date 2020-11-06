import numpy as np
import neural_network
import time
import matplotlib.pyplot as plt

def f(x):
    return x**3+2
# np.random.seed(10)
x = np.random.randn(1,200)
y = f(x)

hyper_parameters = {"size":{0:1,1:3,2:5,3:1},"m":16,"activation":{1:"Leaky ReLU",2:"Leaky ReLU",3:"linear"},"alpha":0.01}

nn = neural_network.initilize(hyper_parameters)

L = np.array([])

t1 = time.time()
for i in range(100000):
    mini_batch = np.random.choice(x.size,hyper_parameters["m"],replace=True)
    yhat = nn.forward_prop(x[np.newaxis,0,mini_batch])

    dL_dyhat = 2*(yhat - y[np.newaxis,0,mini_batch])

    nn.backward_prop(dL_dyhat)

    L = np.append(L,np.sum((nn.forward_prop(x) - y)**2)/hyper_parameters["m"])

t2 = time.time()

print(f(0.25))
print(nn.forward_prop(0.25))

# print(L)
plt.plot(L)
plt.show()
