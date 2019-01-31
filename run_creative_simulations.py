import numpy as np

from smart_home import SmartHome
from v2.control_home import ControlHome
from v2.creative_home import CreativeHome
from v2.adaptive_home import AdaptiveHome
import sys

WIDTH = 20
HEIGHT = 20

# each config is 2-tuple: (name, used awarenesses), where used awarenesses is 5-tuple of booleans in order:
# strategy, goal, resource, context, domain
awareness_configs = [('goal-resource',[True, True, True, False, False, False]),('goal-resource-context-domain', [True, True, True, True, True, False]), ('goal-resource-context-domain-time', [True, True, True, True, True, True])]
# How many times each configs run is repeated
runs_per_config = 5
# Collect stats from all runs of all configs
stats = {}


# Run each config
for config in awareness_configs:
    name = config[0]
    pickle_file = "stats_{}.pkl".format(name)
    awarenesses = config[1]
    stats[name] = {'times': [], 'fitnesses': []}

    for r in range(runs_per_config):
        creative_home = CreativeHome(WIDTH, HEIGHT, awarenesses, pickle_file=pickle_file, show_ani=False)
        creative_home.run()
        stats[name]['times'].append(creative_home.stats['time'])
        stats[name]['fitnesses'].append(creative_home.stats['fitness'])
        stats[name]['logbook'] = creative_home.stats['logbook']

    #print('{} AVGs fitness:{} time:{}'.format(name, np.mean(stats[name]['fitnesses']), np.mean(stats[name]['times'])))


for name, values in stats.items():
    print("'{}' AVGs of the best fitness: {} and time: {}".format(name, np.mean(values['fitnesses']), np.mean(values['times'])))









