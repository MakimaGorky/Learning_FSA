from solution import *

dfa = DFA()
data = [
    ("abc", True),
    ("abd", True),
    ("bcd", False),
    ("ab", True),
]


boot_id = 2
ind = 0
for string, accepted in data:
    dfa.add_string(string, accepted)
    dot = dfa.visualize()
    dot.render(f'{boot_id}-{ind} automaton_step_{string}', format='png', cleanup=True)
    ind += 1
dfa.minimize()
dot = dfa.visualize()
dot.render(f'{boot_id}-{ind} automaton_final_step', format='png', cleanup=True)