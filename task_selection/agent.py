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
        self.successes = {task:0 for task in self.tasks}
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
            
    def select_task(self, common_good_levels, picked_props, t):
        if self.task:
            return
        agent_levels = {prop: self.state[prop]-self.needs[prop][0] for prop in self.state.keys()}
        greatest_need_agent_prop = self.choose_greatest_need(agent_levels)
        greatest_need_agent = self.state[greatest_need_agent_prop] - self.needs[greatest_need_agent_prop][0]
        greatest_need_group_prop = self.choose_greatest_need(common_good_levels)
        #greatest_need_group_prop = min(common_good_levels, key=common_good_levels.get)
        greatest_need_group = common_good_levels[greatest_need_group_prop]

        if greatest_need_group < -1000:
            need = greatest_need_group_prop
        else:
        # if greatest_need_agent > 0 and greatest_need_group > 0:
            avg_skills = self.get_average_skill_for_property()
            #avg_skills = {prop: avg_skills[prop]+1 for prop in avg_skills.keys()}
            total_skills = np.sum([avg_skills[prop] for prop in self.needs.keys()])
            if total_skills == 0:
                probs = [1/len(self.needs) for need in self.needs]
            else:
                probs = [avg_skills[prop]/total_skills for prop in self.needs.keys()]
            need = np.random.choice(list(self.needs.keys()), 1, p=probs)[0]
        # elif greatest_need_group > 0:
        #     need = greatest_need_agent_prop
        # elif greatest_need_agent > 0:
        #     need = greatest_need_group_prop
        # else:
        #     if len(picked_props) > 0:
        #         picked_agent_prop = 0
        #         picked_group_prop = 0
        #         for prop in picked_props:
        #             if prop == greatest_need_agent_prop:
        #                 picked_agent_prop += 1
        #             if prop == greatest_need_group_prop:
        #                 picked_group_prop += 1
        #         total_picked = picked_agent_prop + picked_group_prop
        #         if total_picked > 0:
        #             prop_ratio_agent = picked_agent_prop / total_picked
        #             prop_ratio_group = picked_group_prop / total_picked
        #         else:
        #             prop_ratio_agent = 0
        #             prop_ratio_group = 0
        #     else:
        #         prop_ratio_agent = 0
        #         prop_ratio_group = 0
        #     greatest_need_agent = np.absolute(greatest_need_agent)
        #     greatest_need_group = np.absolute(greatest_need_group)
        #     if greatest_need_agent > greatest_need_group:
        #         prob = max(max((greatest_need_agent-greatest_need_group) / greatest_need_agent, self.social_choice_prob) - prop_ratio_agent, 0)
        #     else:
        #         prob = max((greatest_need_group-greatest_need_agent) / greatest_need_group - prop_ratio_group, 0)
        #     probs = [1-prob, prob]
        #     need = np.random.choice([greatest_need_agent_prop, greatest_need_group_prop], 1, p=probs)[0]
        relevant_tasks = self.property_task_mapping[need]
        skill_total = np.sum([self.successes[task] for task in relevant_tasks])
        if skill_total == 0:
            skill_prob = [1/len(relevant_tasks) for task in relevant_tasks]
        else:
            skill_prob = [self.successes[task]/skill_total for task in relevant_tasks]
        self.task = np.random.choice(relevant_tasks, 1, p=skill_prob)[0]
        self.task_start = t
        self.task_history.append(self.task.id)

    def execute_task(self, t):
        common_reward = {}
        if self.task:
            reward, complete, success = self.task.execute(t,self.task_start,self.successes[self.task], self.experience[self.task])
            if complete:
                self.experience[self.task] += 1
                self.successes[self.task] += 1 if success else 0
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
                #print(f"{self.idx}-{self.task_history}")
                print(f"{self.idx}-{need}:{self.state[need]}, skills:{self.get_tasks_summary()}")

    def is_alive(self):
        return self.alive

    def get_average_skill_for_property(self):
        prop_skill = {}
        for prop in self.property_task_mapping.keys():
            skills = []
            for task in self.property_task_mapping[prop]:
                if self.experience[task] == 0:
                    skills.append(0)
                else:
                    skills.append(self.successes[task]/self.experience[task])
            prop_skill[prop] = np.average(skills)
        return prop_skill
        #return {prop:np.average([self.successes[task] for task in self.property_task_mapping[prop]]) for prop in self.property_task_mapping.keys()}

    def choose_greatest_need(self, levels):
        min_val = None
        props = []
        for prop in levels.keys():
            if min_val == None:
                min_val = levels[prop]
                props = [prop]
            elif min_val > levels[prop]:
                min_val = levels[prop]
                props = [prop]
            elif min_val == levels[prop]:
                props.append(prop)
        return np.random.choice(props, 1)[0]

    def get_state_summary(self):
        return ", ".join([f"{prop.value}: {self.state[prop]}" for prop in self.state.keys()])
    
    def get_tasks_summary(self):
        return ", ".join([f"{task.id}: exp-{self.experience[task]}, skill-{self.successes[task]}" for task in self.tasks])
    
    def print_summary(self):
        print(f"A{self.idx}: state - {self.get_state_summary()}, tasks - {self.get_tasks_summary()}")