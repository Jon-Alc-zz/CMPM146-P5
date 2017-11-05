import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time
from heapq import heappop, heappush

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])


class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key__(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key__())

    def __lt__(self, other):
        return self.__key__() < other.__key__()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].

        consumeFailed = False
        requireFailed = False

        print(rule)
        
        if 'Consumes' in rule: # if current rule consumes something
            for ruleItem in rule['Consumes']: # for each item being consumed
                for stateItem in state.__key__():
                    if stateItem[0] == ruleItem: # check if the items match
                        if stateItem[1] >= rule['Consumes'][ruleItem]: # check if we have enough
                            temp = stateItem[1]
                            stateItem = (stateItem[0], temp - rule['Consumes'][ruleItem])
                        else:
                            consumeFailed = True
                            break
                if consumeFailed:
                    return False

        if 'Requires' in rule: # if current rule requires something
            for ruleItem in rule['Requires']: # for each item is required
                for stateItem in state.__key__():
                    if stateItem[0] == ruleItem:
                        if stateItem[1] <= 1:
                            requireFailed = True
                            break
            if requireFailed:
                return False

        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        if 'Consumes' in rule: # if current rule consumes something
            for ruleItem in rule['Consumes']: # for each item being consumed
                for stateItem in state.__key__():
                    if stateItem[0] == ruleItem: # check if the items match
                        temp = stateItem[1]
                        stateItem = (stateItem[0], temp - rule['Consumes'][ruleItem])
        
        for ruleItem in rule['Produces']: # for each item being produced
            for stateItem in state.__key__():
                if stateItem[0] == ruleItem:
                    temp = stateItem[1]
                    stateItem = (stateItem[0], temp + rule['Produces'][ruleItem])
                    state[stateItem[0]] += stateItem[1]

        next_state = state.copy()
        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for goalItem in Crafting["Goal"]: # for each item in goal
            for stateItem in state.__key__(): # for each item in state
                if goalItem == stateItem[0]: # if current items match
                    if Crafting["Goal"][goalItem] > state[stateItem[0]]: # if quantity is met
                        return False

        return true

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.

    for r in all_recipes:
        if r.check(state):
            # print(r)
            yield (r.name, r.effect(state), r.cost)


def heuristic(state):
    # Implement your heuristic here!
    return 0

def search(graph, state, is_goal, limit, heuristic):

    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    
    frontier = []
    frontier.append(state.copy())
    came_from = {}
    came_from[frontier[0]] = True
    while time() - start_time < limit and not len(frontier) == 0:
        current = frontier.pop(0)
        for next in graph(current):
            if next not in came_from:
                frontier.append(next[1])
                came_from[next[1]] = current

        if is_goal(state):
            came_from
        
    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print('came_from: ', came_from)
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)
    # # List of items that can be in your inventory:
    print('All items:', Crafting['Items'])

    # # List of items in your initial inventory with amounts:
    print('Initial inventory:', Crafting['Initial'])

    # # List of items needed to be in your inventory at the end of the plan:
    print('Goal:',Crafting['Goal'])

    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']}) # initialize values to 0
    # state2 = State({key: 3 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # print(state2.__key__())

    # for r in all_recipes:
    #     print(r.name)
    #     print(r.check(state2.copy()))
        

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 5, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)
