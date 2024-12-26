from FSA import *

dfa = DFA()
data = [
    ("abc", True),
    ("abd", True),
    ("bcd", False),
    ("ab", True),
]


boot_id = 4
img_folder = 'img/'

ind = 0
for string, accepted in data:
    dfa.add_string(string, accepted)
    dot = dfa.visualize()
    dot.render(img_folder + f'{boot_id}-{ind} automaton_step_{string}', format='png', cleanup=True)
    ind += 1
dfa.minimize()
dot = dfa.visualize()
dot.render(img_folder + f'{boot_id}-{ind} automaton_final_step', format='png', cleanup=True)