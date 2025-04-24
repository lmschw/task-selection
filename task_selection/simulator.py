import numpy as np

from task_selection.agent import Agent
from task_selection.properties import Property
from task_selection.task import Task

class TaskBiddingSimulator:
    def __init__(self, n_agents:int, common_goods:dict[Property,list[float]], overall_properties:list[Property], 
                 consumption_rates:dict[Property,float], tasks:list[Task], needs:dict[Property,list[float]], 
                 social_choice_prob:float):
        self.n_agents = n_agents
        self.common_goods = common_goods # prop: current, desired
        self.overall_properties = overall_properties 
        self.consumption_rates = consumption_rates
        self.tasks = tasks
        self.needs = needs # prop: min, max
        self.social_choice_prob = social_choice_prob

        self.initialise()

    def initialise(self):
        self.property_task_mapping = {prop:[task for task in self.tasks if task.property == prop] for prop in self.overall_properties}

        # create agents
        self.agents:list[Agent] = [Agent(idx=i, 
                                         common_good_types=self.common_goods.keys(),
                                         tasks=self.tasks, 
                                         needs=self.needs, 
                                         consumption_rates=self.consumption_rates,
                                         social_choice_prob=self.social_choice_prob,
                                         property_task_mapping=self.property_task_mapping) 
                                    for i in range(self.n_agents)]
        

    def consume_goods(self):
        requests = {agent.idx: agent.request_resources() for agent in self.agents}
        granted = {agent.idx: {good: False for good in self.common_goods} for agent in self.agents}
        for i, good in enumerate(self.common_goods.keys()):
            reqs = [request[good] for request in requests.values()]
            requested = np.sum(reqs)
            if requested <= self.common_goods[good][0]:
                for agent in self.agents:
                    granted[agent.idx][good] = True
                self.common_goods[good][0] -= requested
            else:
                sorted_requests = np.sort(reqs)
                sorted_requests_idx = np.argsort(reqs)
                chosen = []
                sum_reqs = 0
                for j in range(len(sorted_requests)):
                    sum_reqs += sorted_requests[j]
                    if sum_reqs <= self.common_goods[good][0]:
                        chosen.append(sorted_requests_idx[j])
                    else:
                        self.common_goods[good][0] -= sum_reqs - sorted_requests[j]
                for agent_idx in chosen:
                    granted[agent_idx][good] = True
        for agent in self.agents:
            agent.check_granted_consumption_requests(requests[agent.idx], granted[agent.idx])

    def select_tasks(self):
        common_good_levels = {}
        for good, vals in self.common_goods.items():
            current, desired = vals
            common_good_levels[good] = current - desired
        for agent in self.agents:
            agent.select_task(common_good_levels)

    def execute_tasks(self,t):
        for agent in self.agents:
            resource_changes = agent.execute_task(t)
            for good in resource_changes.keys():
                self.common_goods[good][0] += resource_changes[good]

    def update_agent_population(self):
        agents = []
        for agent in self.agents:
            agent.regular_update()
            if agent.is_alive():
                agents.append(agent)
        self.agents = agents

    def simulate(self, tmax):
        for t in range(tmax):
            # consume goods as necessary
            self.consume_goods()
            # select tasks
            self.select_tasks()
            # execute tasks
            self.execute_tasks(t)
            # update stats & kill agents if necessary
            self.update_agent_population()

            if len(self.agents) == 0:
                print(f"ALL AGENTS ARE DEAD at t={t}")
                print(", ".join(f"{good.value}:{self.common_goods[good]}" for good in self.common_goods.keys()))
                break
        print([agent.print_summary() for agent in self.agents])
