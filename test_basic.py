from task_selection.agent import Agent
from task_selection.properties import Property
from task_selection.simulator import TaskBiddingSimulator
from task_selection.task import Task

n_agents = 20
common_goods = {Property.FOOD: [100, 15],
                Property.SHELTER: [100, 15]}
overall_propertiees = [Property.FOOD, Property.SHELTER, Property.REST]
crate = 0
consumption_rates = {Property.FOOD: crate,
                     Property.SHELTER: crate,
                     Property.REST: 0}

reward = 20
duration = 5
task1 = Task("collect_long", Property.FOOD, duration=duration, reward=reward)
task2 = Task("collect_short", Property.FOOD, duration=5, reward=5)
task3 = Task("shelter", Property.SHELTER, duration=duration, reward=reward)
task4 = Task("rest", Property.REST, duration=duration, reward=20)
tasks = [task1, task3]

needs = {Property.FOOD: [15, 20],
         Property.SHELTER: [15, 20]}

social_choice_prob = 0.1

sim = TaskBiddingSimulator(n_agents=n_agents,
                           common_goods=common_goods,
                           overall_properties=overall_propertiees,
                           consumption_rates=consumption_rates,
                           tasks=tasks,
                           needs=needs,
                           social_choice_prob=social_choice_prob)

sim.simulate(tmax=50000)