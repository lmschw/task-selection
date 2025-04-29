import numpy as np

from task_selection.agent import Agent
from task_selection.properties import Property
from task_selection.simulator import TaskBiddingSimulator
from task_selection.task import Task

n_agents = 50
common_goods = {Property.FOOD: [100, 15],
                Property.SHELTER: [100, 15],
                Property.WATER: [100, 15],
                Property.SECURITY: [100, 15],
                Property.COMPANY: [100, 15],
                Property.WASTE_MANAGEMENT: [100, 15]}
overall_propertiees = [Property.FOOD, Property.SHELTER, Property.WATER, Property.SECURITY, Property.COMPANY, Property.WASTE_MANAGEMENT]
crate = 0.1
consumption_rates = {Property.FOOD: crate,
                     Property.SHELTER: crate,
                     Property.WATER: crate,
                     Property.SECURITY: crate,
                     Property.COMPANY: crate,
                     Property.WASTE_MANAGEMENT: crate}

reward = 40
duration = 5
task1 = Task("collect_long", Property.FOOD, duration=duration, reward=reward)
task2 = Task("collect_short", Property.FOOD, duration=5, reward=5)
task3 = Task("shelter", Property.SHELTER, duration=duration, reward=reward)
task4 = Task("rest", Property.REST, duration=duration, reward=50)
task5 = Task("water", Property.WATER, duration=duration, reward=reward)
task6 = Task("guard", Property.SECURITY, duration=duration, reward=reward)
task7 = Task("chill", Property.COMPANY, duration=duration, reward=reward)
task8 = Task("shovel_shit", Property.WASTE_MANAGEMENT, duration=duration, reward=reward)
tasks = [task1, task2, task3, task5, task6, task7, task8]

needs = {Property.FOOD: [15, 20],
         Property.SHELTER: [15, 20],
         Property.WATER: [15,20],
         Property.SECURITY: [15, 20],
         Property.COMPANY: [15, 20],
         Property.WASTE_MANAGEMENT: [15, 20]}

social_choice_prob = 0.1
tmax = 50000


survived = []
survival_rates = []
chose_f = []
perc_f = []
chose_s = []
perc_s = []
time_spent_f_if_f = []
perc_time_f = []
time_spent_s_if_s = []
perc_time_s = []
num_iters = 1
for i in range(num_iters):
    sim = TaskBiddingSimulator(n_agents=n_agents,
                            common_goods=common_goods,
                            overall_properties=overall_propertiees,
                            consumption_rates=consumption_rates,
                            tasks=tasks,
                            needs=needs,
                            social_choice_prob=social_choice_prob)

    exp, succ = sim.simulate(tmax=tmax)
    survived.append(len(exp))
    survival_rates.append(len(exp)/n_agents)
    f = 0
    s = 0
    time_spent_f = 0
    time_spent_s = 0
    for i in range(len(exp)):
        if exp[i][task1] > exp[i][task3]:
            f += 1
            time_spent_f += duration * exp[i][task1]
        else:
            s += 1
            time_spent_s += duration * exp[i][task3]
    chose_f.append(f)
    chose_s.append(s)
    perc_f.append(f/len(exp))
    perc_s.append(s/len(exp))
    time_spent_f_if_f.append(time_spent_f)
    time_spent_s_if_s.append(time_spent_s)
    perc_time_f.append(time_spent_f/tmax)
    perc_time_s.append(time_spent_s/tmax)

print(f"survival rate: {np.average(survival_rates)}, total survived: {np.sum(survived)}, total survival rate: {np.sum(survived)/(num_iters*n_agents)}")
print(f"chose f %: {np.sum(f)/(num_iters*n_agents)}, avg %: {np.average(perc_f)}")
print(f"chose s %: {np.sum(s)/(num_iters*n_agents)}, avg %: {np.average(perc_s)}")
print(f"time f %: {np.sum(time_spent_f_if_f)/(num_iters*tmax)}, avg %: {np.average(perc_time_f)}")
print(f"time s %: {np.sum(time_spent_s_if_s)/(num_iters*tmax)}, avg %: {np.average(perc_time_s)}")