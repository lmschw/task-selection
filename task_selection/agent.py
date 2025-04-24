import numpy as np
import random

from task_selection.properties import Property
from task_selection.task import Task

class Agent:
    def __init__(self, idx:int, common_good_types:list[Property], tasks:list[Task], needs:dict[Property,float], 
                 consumption_rates:dict[Property,float], social_choice_prob:float, property_task_mapping:dict[Property,list[Task]]):
        self.idx = idx
        self.common_good_types = common_good_types
        self.tasks = tasks
        self.needs = needs
        self.consumption_rates = consumption_rates
        self.social_choice_prob = social_choice_prob
        self.property_task_mapping = property_task_mapping

        self.initialise()

    def initialise(self):
        self.state = {need:np.average([self.needs[need][0], self.needs[need][1]]) for need in self.needs.keys()}
        self.skills = {task:0 for task in self.tasks}
        self.experience = {task:0 for task in self.tasks}
        self.alive = True
        self.task:Task = None

        self.task_history = []

    def request_resources(self):
        requests = {}
        for good in self.common_good_types:
            req = 0
            for need in self.needs.keys():
                if need == good:
                    if self.state[need] < self.needs[need][0]:
                        req += self.needs[need][0] - self.state[need]
            requests[good] = req
        return requests

    def check_granted_consumption_requests(self, requests, grants):
        for prop in grants.keys():
            if grants[prop]:
                self.state[prop] += requests[prop]
            
    def select_task(self, common_good_levels):
        if self.task:
            return
        greatest_need_agent_prop = min(self.state, key=self.state.get)
        greatest_need_agent = self.state[greatest_need_agent_prop]
        greatest_need_group_prop = min(common_good_levels, key=common_good_levels.get)
        greatest_need_group = np.absolute(common_good_levels[greatest_need_group_prop])

        if greatest_need_agent_prop == greatest_need_group_prop or common_good_levels[greatest_need_group_prop] > 0:
            need = greatest_need_agent_prop
        else:
            if greatest_need_agent > greatest_need_group:
                prob = max((greatest_need_agent-greatest_need_group) / greatest_need_agent, self.social_choice_prob)
            else:
                prob = (greatest_need_group-greatest_need_agent) / greatest_need_group
            probs = [1-prob, prob]
            need = np.random.choice([greatest_need_agent_prop, greatest_need_group_prop], 1, p=probs)[0]
        relevant_tasks = self.property_task_mapping[need]
        skill_total = np.sum([self.skills[task] for task in relevant_tasks])
        if skill_total == 0:
            skill_prob = [1/len(relevant_tasks) for task in relevant_tasks]
        else:
            skill_prob = [self.skills[task]/skill_total for task in relevant_tasks]
        self.task = np.random.choice(relevant_tasks, 1, p=skill_prob)[0]
        self.task_history.append(self.task.id)

    def execute_task(self, t):
        common_reward = {}
        if self.task:
            reward, complete, success = self.task.execute(t, self.skills[self.task])
            if complete:
                self.experience[self.task] += 1
                self.skills[self.task] += 1 if success else 0
                self.task = None
            for prop in reward.keys():
                if prop in self.common_good_types:
                    common_reward[prop] = reward[prop]
                else:
                    self.state[prop] += reward[prop]
        return common_reward

    def regular_update(self):
        for need in self.needs.keys():
            self.state[need] -= self.consumption_rates[need]
            if self.state[need] <= 0:
                self.alive = False

    def is_alive(self):
        return self.alive
    
    def get_state_summary(self):
        return ", ".join([f"{prop.value}: {self.state[prop]}" for prop in self.state.keys()])
    
    def get_tasks_summary(self):
        return ", ".join([f"{task.id}: exp-{self.experience[task]}, skill-{self.skills[task]}" for task in self.tasks])
    
    def print_summary(self):
        print(f"A{self.idx}: state - {self.get_state_summary()}, tasks - {self.get_tasks_summary()}")