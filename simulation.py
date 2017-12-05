from model import *
from math import exp


T = 10000
tau_param = (0, 0.8)
task_package = [1, 2, 4, 3]
params_for_generators = {1: (4, 2), 2: (8, 2), 3: (0.1, 1), 4: (-0.3, 0.25)}
module_config = {1: 2, 2: 2, 3: 2, 4: 2}
generators = {1: random.betavariate, 2: random.betavariate, 3: random.uniform, 4: random.lognormvariate}
task_generator = random.uniform

a, b = tau_param
print('task mw', (a+b)/2, 'd', (pow(b - a + 1, 2) - 1) / 12)
a, b = params_for_generators[1]
print(1, 'mw', a/(a+b), 'd', a*b/(pow(a+b, 2)*(a+b+1)))
a, b = params_for_generators[2]
print(2, 'mw', a/(a+b), 'd', a*b/(pow(a+b, 2)*(a+b+1)))
a, b = params_for_generators[3]
print(3, 'mw', (a+b)/2, 'd', (pow(b - a + 1, 2) - 1) / 12)
mu, sigma = params_for_generators[4]
print(4, 'mw', exp(mu + sigma*sigma / 2), 'd', (exp(sigma*sigma) - 1)*exp(2*mu + sigma*sigma))

model1 = Model(T,task_package,generators,params_for_generators,task_generator,tau_param,module_config)
model1.start()
