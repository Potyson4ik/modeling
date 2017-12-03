from model import *
from math import exp


T = 10000
tau_param = (0, 0.8)
task_package = [1, 2, 4, 3]
params_for_generators = {1: (8, 2), 2: (8, 2), 3: (0.1, 1), 4: (-0.2, 0.25)}
module_config = {1: 2, 2: 2, 3: 2, 4: 2}
generators = {1: random.betavariate, 2: random.betavariate, 3: random.uniform, 4: random.lognormvariate}
task_generator = random.uniform

# Создание и инициализация сервера
server = Server(params_for_generators, generators, module_config)

system_time = 0
is_time_of_task = True
task_time = task_generator(*tau_param)
system_time = task_time
task = Task(task_package[:], task_time)

a, b = tau_param
print('task', a, b, 'mw', (a+b)/2, 'd', (pow(b - a + 1, 2) - 1) / 12)
a, b = params_for_generators[1]
print(1, a, b, 'mw', a/(a+b), 'd', a*b/(pow(a+b, 2)*(a+b+1)))
a, b = params_for_generators[2]
print(2, a, b, 'mw', a/(a+b), 'd', a*b/(pow(a+b, 2)*(a+b+1)))
a, b = params_for_generators[3]
print(3, a, b, 'mw', (a+b)/2, 'd', (pow(b - a + 1, 2) - 1) / 12)
mu, sigma = params_for_generators[4]
print(4, mu, sigma, 'mw', exp(mu + sigma*sigma / 2), 'd', (exp(sigma*sigma) - 1)*exp(2*mu + sigma*sigma))

task_counter = 1
while system_time is None or system_time < T:
    # print('g1',generators[1](*params_for_generators[1]))
    # print('g2', generators[2](*params_for_generators[2]))
    # print('g3', generators[3](*params_for_generators[3]))
    # print('g4', generators[4](*params_for_generators[4]))
    if system_time is None or system_time >= task_time:
        server.add_task(task)
        task_time += task_generator(*tau_param)
        task = Task(task_package[:], task_time)
        task_counter += 1
    else:
        server.next_event()
    system_time = server.get_nearest_event_time()

print('Задачи принятые сервером', task_counter)
print('Обработано задач', len(server.output_tasks))
info = ""
for modules in server.modules.values():
    for module in modules:
            info += """m({})[{}]:
                        t{}:wt:{};\n""".format(module.resource_type,
                                                               len(module.queue),
                                                               module.time,
                                                               module.wait_time)
print(info)