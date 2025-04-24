from task_selection.agent import Agent
from task_selection.properties import Property
from task_selection.simulator import TaskBiddingSimulator
from task_selection.task import Task

n_agents = 10
common_goods = {Property.FOOD: [10, 15],
                Property.SHELTER: [10, 15]}
overall_propertiees = [Property.FOOD, Property.SHELTER, Property.REST]
consumption_rates = {Property.FOOD: 0.1,
                     Property.SHELTER: 0.1,
                     Property.REST: 0.5}

task1 = Task("collect_long", Property.FOOD, duration=10, reward=10)
task2 = Task("collect_short", Property.FOOD, duration=5, reward=5)
task3 = Task("shelter", Property.SHELTER, duration=10, reward=10)
task4 = Task("rest", Property.REST, duration=10, reward=40)
tasks = [task1, task3, task4]

needs = {Property.FOOD: [10, 20],
         Property.SHELTER: [15, 20],
         Property.REST: [20, 100]}

social_choice_prob = 0.5

sim = TaskBiddingSimulator(n_agents=n_agents,
                           common_goods=common_goods,
                           overall_properties=overall_propertiees,
                           consumption_rates=consumption_rates,
                           tasks=tasks,
                           needs=needs,
                           social_choice_prob=social_choice_prob)

sim.simulate(tmax=500)