from FSA import *
from App import *

# dfa = DFA()
# dfa.undefined_string_acception_type = 'Soft'
# data = [
#     ("abc", True),
#     ("abd", True),
#     ("bcd", False),
#     ("ab", True),
#     ("abca", False),
#     ("abcaa", True),
#     ("abda", True),  # abca - False conflict
# ]
# #
# #
# boot_id = 7
# img_folder = ''  #'img/'
#
# ind = 0
# for string, accepted in data:
#     dfa.add_string(string, accepted)
#     dot = dfa.visualize()
#     dot.render(img_folder + f'{boot_id}-{ind} automaton_step_{string}', format='png', cleanup=True)
#     print(f'{ind} state added')
#     ind += 1
# dfa.minimize()
# dot = dfa.visualize()
# dot.render(img_folder + f'{boot_id}-{ind} automaton_final_step', format='png', cleanup=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutomataApp(root)
    root.mainloop()