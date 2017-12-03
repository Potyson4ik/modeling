import random


class Task:
    def __init__(self, task_package, current_time):
        self.resources = task_package  # Пакет ресурсов, которые содержит задача
        self.runtime = 0  # Время обработки задачи
        self.wait_time = 0  # Время ожидания задачи в очереди
        self.time = current_time  # Системное время
        self.is_run = False  # True - задача в данный момент обрабатывается севером
        self.resource = self.resources[0]  # Текущий обрабатываемый ресурс задачи

    # Метод возвращает время обработки задачи на сервере
    def get_total_time(self):
        return self.runtime + self.wait_time

    # Метод запускает выполнение задачи
    def run_task(self, time):
        self.resource = self.resources.pop(0)
        self.wait_time += time - self.time
        self.time = time
        self.is_run = True
        return self.runtime

    # Метод останавливает выполнение задачи
    def stop_task(self, time):
        self.runtime += time - self.time
        self.time = time
        self.task_run = False

    # Метод возвращет текущий обрабатываемый ресурс задачи
    def get_resource(self):
        return self.resource

    # Метод возвращает следующий обрабатываемый ресурс задачи
    def get_next_resource(self):
        if len(self.resources) > 0:
            return self.resources[0]
        return None

class Module:
    def __init__(self, resource_type, generator, generator_param):
        self.resource_type = resource_type  # Тип ресурса, который модуль может обрабатывать
        self.generator = generator  # Генератор времени обработки ресурса
        self.generator_param = generator_param  # Входные параметры для генератора
        self.busy = False  # True - если модуль обрабатывает ресурс
        self.queue = []  # Очередь задач модуля
        self.time = 0  # Время работы модуля
        self.task = None  # Текущая задача
        self.wait_time = 0  # Время бездействия модуля
        self.wait_time_list = []  # Список промежутков времени бездействия модуля
        self.task_time_list = []  # Список промежутков времени поступления задач в модуль
        self.module_time_list = []  # Список промежутков времени обработки задач модулем


    # Метод добавляет задачу в модуль
    def add_task(self, task):
        if self.busy:
            self.queue.append(task)
        else:
            time = task.time
            task.run_task(time)
            self.wait_time_list.append(time - self.time)
            self.wait_time += time - self.time
            task_time = self.generator(*self.generator_param)
            self.task_time_list.append(task_time)
            time += task_time
            self.task = task
            self.time = time
            self.busy = True

    # Метод завершает обработку текущей задачи и запускает следующую задачу (при наличии задачи в очереди)
    def next_task(self):
        if self.busy:
            completed_task = self.task
            completed_task.stop_task(self.time)
            if len(self.queue) == 0:
                self.busy = False
                self.task = None
            else:
                task = self.queue.pop(0)
                task_time = self.generator(*self.generator_param)
                self.task_time_list.append(task_time)
                task.run_task(self.time)
                self.task = task
                self.time += task_time
                self.busy = True
            return completed_task
        return None


class Server:
    def __init__(self, generators_param, generators, module_config):
        self.modules = {}  # Модули
        self.generators = generators  # Генераторы времён обработки ресурсов
        self.generators_param = generators_param  # Входные параметры для генераторов
        self.time = 0  # Время работы сервера
        self.output_tasks = []  # Список завершенных задач
        # Инициализация модулей по заданной конфигурации
        for key, module_count in module_config.items():
            if key not in self.modules:
                self.modules[key] = []
            for i in range(module_count):
                self.modules[key].append(Module(key, self.generators[key], self.generators_param[key]))

    # Метод добавляет задачу на сервер
    def add_task(self, task):
        task_resource = task.get_resource()
        module_list = self.modules[task_resource]
        selected_module_index = None
        min_queue_size = None
        for i in range(len(module_list)):
            module = module_list[i]
            if not module.busy:
                selected_module_index = i
                break
            elif selected_module_index is None or min_queue_size > len(module.queue):
                selected_module_index = i
                min_queue_size = len(module.queue)
        module = module_list[selected_module_index]
        module.add_task(task)
        self.modules[task_resource][selected_module_index] = module

    # Метод возвращает индекс модуля, вида - (<тип ресурса>, <номер модуля в списке>)
    def _get_module_index_by_nearest_event(self):
        min_module_time = None
        module_index = None
        for key, module_list in self.modules.items():
            for i in range(len(module_list)):
                module = module_list[i]
                if (min_module_time is None or module.time < min_module_time) and module.time > 0 and module.busy:
                    min_module_time = module.time
                    module_index = (key, i)
        return module_index
    # Метод возвращает время ближайшего события на сервере
    def get_nearest_event_time(self):
        min_module_time = None
        for module_list in self.modules.values():
            for module in module_list:
                if (min_module_time is None or module.time < min_module_time) and module.time > 0 and module.busy:
                    min_module_time = module.time
        return min_module_time
    # Метод выполняет следующее событие
    def next_event(self):
        key, index = self._get_module_index_by_nearest_event()
        task = self.modules[key][index].next_task()
        if task is not None:
            if task.get_next_resource() is not None:
                module_index = None
                min_queue_size = None
                next_resource = task.get_next_resource()
                for i in range(len(self.modules[next_resource])):
                    module = self.modules[next_resource][i]
                    if not module.busy:
                        module_index = i
                        break
                    if min_queue_size is None or min_queue_size > len(module.queue):
                        module_index = i
                        min_queue_size = len(module.queue)
                self.modules[next_resource][module_index].add_task(task)
            else:
                self.output_tasks.append(task)