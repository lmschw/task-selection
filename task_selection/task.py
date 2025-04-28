import random

from task_selection.properties import Property

class Task:
    def __init__(self, id:str, property:Property, duration:int, reward:float, min_threshold:float=0.1):
        self.id = id
        self.property = property
        self.duration = duration
        self.reward = reward
        self.min_threshold = min_threshold

    def execute(self, t, start_t, skill_level, experience):
        complete = False
        success = False
        reward = 0
        if t - start_t >= self.duration:
            complete = True
            if skill_level == 0 or experience == 0:
                threshold = 0.1
            else:
                threshold = skill_level/experience

            skill_impact = 1-skill_level/experience if skill_level != 0 else 0
            #threshold = max(1 - skill_impact, self.min_threshold)
            r = random.random()
            if r <= threshold:
                success = True
            if success:
                reward = self.reward
        return {self.property: reward}, complete, success
