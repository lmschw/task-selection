import random

from task_selection.properties import Property

class Task:
    def __init__(self, id:str, property:Property, duration:int, reward:float, min_threshold:float=0.1):
        self.id = id
        self.property = property
        self.duration = duration
        self.reward = reward
        self.min_threshold = min_threshold

        self.start_timestep = None

    def execute(self, t, skill_level):
        if not self.start_timestep:
            self.start_timestep = t
        complete = False
        success = False
        reward = 0
        if t - self.start_timestep >= self.duration:
            complete = True
            skill_impact = 1/skill_level if skill_level != 0 else 0
            threshold = max(1 - skill_impact, self.min_threshold)
            r = random.random()
            if r <= threshold:
                success = True
            reward = self.reward
        return {self.property: reward}, complete, success
