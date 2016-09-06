import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
from operator import itemgetter

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.Q = {None: {None: 0}}
        self.trials = [] # To track the results of each trial.

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.prev_state = None
        self.prev_action = None
        self.prev_reward = 0
        self.total_reward = 0

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        light = inputs['light']
        oncoming = inputs['oncoming']
        left = inputs['left']
        right = inputs['right']
        self.state = (light, oncoming, left, right, self.next_waypoint)
        
        # TODO: Select action according to your policy
        a, g, epsilon, initial_Q = (0.83, 0.82, 0.0, 1)

        action_Q_pairs = []
        for action in self.env.valid_actions:
            try:
                self.Q[self.state]
            except KeyError:
                self.Q[self.state] = {}
            try:
                self.Q[self.state][action]
            except KeyError:
                self.Q[self.state][action] = initial_Q
            action_Q_pairs.append((action, self.Q[self.state][action]))
        max_Q = max(action_Q_pairs, key=itemgetter(1))[1]
        top_actions = [action for action, Q in action_Q_pairs if Q == max_Q]
        
        # Find action according to epsilon-greedy, with respect to Q
        actions = []
        for _ in range(int(100 * epsilon)):
            actions.append(random.choice(self.env.valid_actions))
        for _ in range(int(100 * (1 - epsilon))):
            actions.append(random.choice(top_actions))
        action = random.choice(actions)

        # Execute action and get reward
        reward = self.env.act(self, action)
        self.total_reward += reward

        # TODO: Learn policy based on state, action, reward
        r = self.prev_reward
        Q = self.Q[self.prev_state][self.prev_action]
        self.Q[self.prev_state][self.prev_action] = Q + a * (r + g * max_Q - Q)
        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]
        
        self.prev_state = self.state
        self.prev_action = action
        self.prev_reward = reward

def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.0, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
