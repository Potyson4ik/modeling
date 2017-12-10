import matplotlib.pyplot as plt
import random
from math import exp
from model import *

if __name__ == "__main__":
    T = 1000000
    task_gen_param = (0, 0.5)
    task_package = [1, 2, 4, 3]
    params_for_generators = {1: (1.1, 1.2), 2: (1.75, 1.9), 3: (0.45, 0.5), 4: (-0.75, 0.25)}
    module_config = {1: 2, 2: 2, 3: 2, 4: 2}
    generators = {1: random.betavariate, 2: random.betavariate, 3: random.uniform, 4: random.lognormvariate}
    task_generator = random.uniform

    print('Входные параметры:')
    print('Задачи:')
    a, b = task_gen_param
    print('\tМат. ожидание - ', (a+b)/2,
          '; дисперсия - ', (pow(b - a + 1, 2) - 1) / 12, '.')
    print('Модули обработки ресурсов 1-го типа:')
    a, b = params_for_generators[1]
    print('\tМат. ожидание - ', a/(a+b),
          '; дисперсия - ', a*b/(pow(a+b, 2)*(a+b+1)), '.')
    print('Модули обработки ресурсов 2-го типа:')
    a, b = params_for_generators[2]
    print('\tМат. ожидание - ', a/(a+b),
          '; дисперсия - ', a*b/(pow(a+b, 2)*(a+b+1)), '.')
    print('Модули обработки ресурсов 3-го типа:')
    a, b = params_for_generators[3]
    print('\tМат. ожидание - ', (a+b)/2,
          '; дисперсия - ', (pow(b - a + 1, 2) - 1) / 12, '.')
    print('Модули обработки ресурсов 4-го типа:')
    mu, sigma = params_for_generators[4]
    print('\tМат. ожидание - ', exp(mu + sigma*sigma / 2),
          '; дисперсия - ', (exp(sigma*sigma) - 1)*exp(2*mu + sigma*sigma), '.')
    print()

    model = Model(T, task_package, generators, params_for_generators,task_generator, task_gen_param, module_config)
    model.start()

    print('Задачи принятые сервером - ', model.get_input_task_count())
    print('Обработано задач - ', model.get_output_task_count())
    print('Среднее время обработки задачи сервером (без учета ожидания в очери) - ', model.server.get_avg_task_runtime())
    print('Среднее время ожидания задачи в очередях модулей - ', model.server.get_avg_task_wait_time())
    print()
    info = """
    Модуль (тип ресурса - {}, номер - {}):
        Выполнено задач: {};
        Задачи оставшиеся в очереди: {};
        Общее время обработки ресурсов: {};
        Среднее время обработки ресурса: {};
        Время ожидания новых ресурсов: {};
        Среднее время ожидания ресурса: {};
        Максимальное время ожидания ресурса: {};
        Среднее время поступления ресурсов: {};
        Загруженность модуля: {}"""
    for resource, modules in model.server.modules.items():
        for number, module in enumerate(modules):
            print(info.format(resource, number,
                              module.completed_task,
                              len(module.queue),
                              sum(module.module_time_list),
                              module.get_avg_module_time(),
                              module.get_wait_time(),
                              module.get_wait_time() / len(module.wait_time_list),
                              max(module.wait_time_list),
                              module.get_avg_task_time(),
                              module.get_load()))

            plt.figure("ProbModule{}_{}".format(resource, number))
            plt.plot(*model.get_probability_func(module.wait_time_list, len(module.wait_time_list) / 1000))
            plt.title('Функция распределения вероятностей')
            plt.xlabel('Время ожидания модуля')
            plt.ylabel('Вероятность')
            plt.grid(True)
            plt.show()

            plt.figure("DistModule{}_{}".format(resource, number))
            plt.plot(*model.get_distribution_func(module.wait_time_list, len(module.wait_time_list) / 2500))
            plt.title('Функция плотности распределения')
            plt.xlabel('Время ожидания модуля')
            plt.ylabel('Вероятность')
            plt.grid(True)
            plt.show()
        print()