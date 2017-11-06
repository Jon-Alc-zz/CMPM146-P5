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
        
        """
        if 'Requires' in rule:
            for ruleItem in rule['Requires']:
                if state[ruleItem] == 0:
                    return False
        """
        
        # check if the item being produced is in the goal
        for ruleItem in rule['Produces']:
            if state[ruleItem] > 0:
                print(state[ruleItem], ' > 0 ')
                return True
        
        return False

    return check
    
def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        
        if 'Produces' in rule: # if current rule consumes something
            for ruleItem in rule['Produces']: # for each item being consumed
                state[ruleItem] -= rule['Produces'][ruleItem] 
                            
        if 'Consumes' in rule: # if current rule consumes something
            for ruleItem in rule['Consumes']: # for each item being consumed
                state[ruleItem] += rule['Consumes'][ruleItem]                
        
        if 'Requires' in rule:
            for ruleItem in rule['Requires']:
                state[ruleItem] += 1
        
        next_state = state.copy()
        return next_state

    return effect    

def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        lock = False # made this so we can print out ALL the things we have too much of
        # This code is used in the search process and may be called millions of times.
        #for initItem in Crafting['Initial']: # for each item in Initial
        for item in Crafting['Items']: # for every item
            if item in state:
                if state[item] > 0: # if we have more than 0 of any item, we not at 'Init' so return False   
                    #print("GGGGoal not reached because you have: " , item,': ',state[item])
                    lock = True
                    #return False
                    
        if not lock:
            print("hi, you now have nothing!")
            return True

    return is_goal

def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.

    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state.copy()), r.cost)

def heuristic(state):
    # Implement your heuristic here!
    return 0

def search(graph, state, is_goal, limit, heuristic):

    start_time = time()

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    
    start = state.copy()
    frontier = []
    heappush(frontier, (start, 0))
    path = [(start,None)]
    came_from = {}
    came_from[start] = None
    while not len(frontier) == 0 and time() - start_time < limit:
        print("Hi", frontier)
        current = heappop(frontier)
        
        if is_goal(current[0]):
            print('reached goal',current)
            break
               
        for next in graph(current[0].copy()): #.copy() DO COPY
            print('NEXT: ', next)
            if next[1] not in came_from: #next FIX
                heappush(frontier, (next[1], next[2] + current[1]))
                path.append((next[1],next[0]))
                print('did action: ' , next[0])
                came_from[next[1]] = current
    #print('PATH: ',path)
    return path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)
    #print('Goal:',Crafting['Goal'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)

    # Create a function which checks for the goal
    #is_goal = make_goal_checker(Crafting['Goal'])
    is_goal = make_goal_checker(Crafting['Initial'])

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']}) # initialize values to 0
    state.update(Crafting['Goal'])
    print('STARTING AT:',state)

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 5, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state, action)
            #print(action)
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
