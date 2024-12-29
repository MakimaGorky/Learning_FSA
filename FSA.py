from graphviz import Digraph
from itertools import combinations
from collections import defaultdict, deque
import re
import json

class DFA:
    def __init__(self, alphabet=None, states=None, start_state=None, accepting_states=None, stated_transitions=None):
        init_id = 0
        # Strict: Всё, что не разрешено - запрещено / Adaptive: Как было, так и будет / Soft: Всё, что не запрещено - разрешено
        self.undefined_string_acception_type = 'Strict'
        self.accept_empty_word = True

        # self.states = None  # no need
        self.stated_transitions = {init_id: {}} if stated_transitions is None else stated_transitions
        self.start_state = init_id if start_state is None else start_state
        self.accepting_states = {0} if accepting_states is None else accepting_states
        self.new_state_id = init_id + 1  # Уникальные идентификаторы для новых состояний
        self.alphabet = set() if alphabet is None else alphabet  # Изначально молодой и наивный автомат не знает, какому языку ему придётся научиться

    def check_string(self, string):
        cur_state = self.start_state
        for char in string:
            if char not in self.stated_transitions[cur_state]:
                if self.undefined_string_acception_type == 'Strict':
                    return False
                elif self.undefined_string_acception_type == 'Adaptive':
                    return cur_state in self.accepting_states
                elif self.undefined_string_acception_type == 'Soft':
                    return True
            cur_state = self.stated_transitions[cur_state][char]

        return cur_state in self.accepting_states

    def change_acceptance_of_empty_word(self, acceptance):
        self.accept_empty_word = acceptance
        if not acceptance:
            self.accepting_states.remove(self.start_state)
        else:
            self.accepting_states.add(self.start_state)

    def add_string(self, string, accepted):
        current_state = self.start_state
        for char in string:
            if char not in self.alphabet:
                self.alphabet.add(char)
            if char not in self.stated_transitions[current_state]:
                self.stated_transitions[current_state][char] = self.new_state_id
                self.stated_transitions[self.new_state_id] = {}
                self.new_state_id += 1
                new_state_added = True
            current_state = self.stated_transitions[current_state][char]

        if accepted:
            self.accepting_states.add(current_state)
        elif current_state in self.accepting_states:
            self.accepting_states.remove(current_state)

        # self.minimize()

    def visualize_pref(self):
        dot = Digraph()
        for state, transitions in self.stated_transitions.items():
            cur_shape = "doublecircle" if state in self.accepting_states else "circle"
            dot.node(str(state), shape=cur_shape)
            if state == self.start_state:
                dot.edge('', str(state))
            for char, target in transitions.items():
                dot.edge(str(state), str(target), label=char)
        return dot

    def visualize(self):
        dot = Digraph()

        # Костыль для исправления фантомного бага
        added_edges = set()
        # Все узлы
        for state in self.stated_transitions.keys():
            cur_shape = "doublecircle" if state in self.accepting_states else "circle"
            dot.node(str(state), shape=cur_shape)

        # Указатель на стартовое
        dot.node('start', shape='none')
        dot.edge('start', str(self.start_state))

        # Для Soft типа распознавания
        everaccepting_state = str(len(self.stated_transitions))
        if self.undefined_string_acception_type == 'Soft':
            dot.node(everaccepting_state, shape="doublecircle")

        # 🌌 transitions 🌌
        for state in self.stated_transitions:
            for sym in self.alphabet:
                if sym in self.stated_transitions[state]:
                    target_state = self.stated_transitions[state][sym]
                    cur_edge = (str(state), str(target_state), sym)
                    if cur_edge not in added_edges:
                        dot.edge(str(state), str(target_state), label=sym)
                        added_edges.add(cur_edge)
                elif self.undefined_string_acception_type == 'Adaptive':
                    cur_edge = (str(state), str(state), sym)
                    if cur_edge not in added_edges:
                        added_edges.add(cur_edge)
                        dot.edge(str(state), str(state), label=sym)  # ➰ Петля ➰
                                                                     #      4
                                                                     #     www
                elif self.undefined_string_acception_type == 'Soft':
                    cur_edge = (str(state), everaccepting_state, sym)
                    if cur_edge not in added_edges:
                        dot.edge(str(state), everaccepting_state, label=sym)
                        added_edges.add(cur_edge)

        if self.undefined_string_acception_type == 'Soft':
            for sym in self.alphabet:
                cur_edge = (everaccepting_state, everaccepting_state, sym)
                if cur_edge not in added_edges:
                    dot.edge(everaccepting_state, everaccepting_state, label=sym)
                    added_edges.add(cur_edge)

        return dot

    # God save the Hopcroft
    def minimize(self):
        # may be hardcoded to a class for reason
        states = set(self.stated_transitions.keys())

        # 0-equivalence split
        equivalence_classes = [set(self.accepting_states), set(states) - set(self.accepting_states)]
        class_queue = deque([set(self.accepting_states), set(states) - set(self.accepting_states)])  # say no to deepcopy

        while class_queue:
            cur_class = class_queue.popleft()
            for symbol in self.alphabet:
                # States that transit into cur by symbol
                transitables_to_cur = {s for s in states if self.stated_transitions.get(s, {}).get(symbol) in cur_class}

                for eq_class in equivalence_classes[:]:
                    cur_intersect = transitables_to_cur & eq_class
                    cur_diff = eq_class - transitables_to_cur

                    if cur_intersect and cur_diff:
                        equivalence_classes.remove(eq_class)
                        equivalence_classes.append(cur_intersect)
                        equivalence_classes.append(cur_diff)

                        if eq_class in class_queue:
                            class_queue.remove(eq_class)
                            class_queue.append(cur_intersect)
                            class_queue.append(cur_diff)
                        else:
                            if len(cur_intersect) <= len(cur_diff):
                                class_queue.append(cur_intersect)
                            else:
                                class_queue.append(cur_diff)

        def find_equivalence_class(eq_states, state):
            for eq_state in eq_states:
                if state in eq_state:
                    return frozenset(eq_state)
            return None

        # Reconstruction
        new_states = {frozenset(part): i for i, part in enumerate(equivalence_classes)}
        new_stated_transitions = {}
        new_accepting_states = set()
        new_start_state = new_states[find_equivalence_class(equivalence_classes, self.start_state)]

        for eq_class in equivalence_classes:
            new_state = new_states[frozenset(eq_class)]
            if eq_class & self.accepting_states:
                new_accepting_states.add(new_state)

            for state in eq_class:
                if state in self.stated_transitions:
                    if len(self.stated_transitions[state]) == 0:
                        new_stated_transitions[new_state] = {}
                    for symbol, next_state in self.stated_transitions[state].items():
                        new_next_state = new_states[find_equivalence_class(equivalence_classes, next_state)]
                        if new_state not in new_stated_transitions:
                            new_stated_transitions[new_state] = {}
                        new_stated_transitions[new_state][symbol] = new_next_state

        self.stated_transitions = new_stated_transitions
        self.start_state = new_start_state
        self.accepting_states = new_accepting_states

    # dsa.json format:
    #
    # {
    #     "states": ["0", "1", "2"],
    #     "alphabet": ["a", "b"],
    #     "start": 0,
    #     "accepting": ["2"],
    #     "transitions": {
    #         "0": {
    #             "a": ["1"]
    #             "b": ["2"]
    #         },
    #         "1": {
    #             "a": ["2"]
    #         },
    #         "2": {
    #             "b": ["0"]
    #         }
    #     }
    # }
    @staticmethod
    def read_json(file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return DFA(
            alphabet=set(data['alphabet']),
            states=set(map(int, data['states'])),
            start_state=int(data['start']),
            accepting_states=set(map(int, data['accepting'])),
            stated_transitions={
                int(state): {char: int(to_states) for char, to_states in transitions.items()}
                for state, transitions in data['transitions'].items()
            }
        )

    # nfsa.txt format:
    #
    # a, b              ->  alphabet
    # q0, q1, q2        ->  states
    # q0                -> start acceptance
    # q2, q1            -> final states
    # q0, a, q1, q2     ->  transitions from 'q0' with 'a' to 'q1' and 'q2'
    # q0, b, q2         -> etc.
    # q1, a, q2
    # q2, b, q0
    @staticmethod
    def read_txt(file_path):
        with open(file_path, 'r') as file:
            lines = file.readlines()
        alphabet = set([c for c in re.split(r'[,\s]+', lines[0]) if c])
        states = set([int(c) for c in re.split(r'[,\s]+', lines[1]) if c])
        start_state = int(lines[2].strip())
        accepting_states = set([int(c) for c in re.split(r'[,\s]+', lines[3]) if c])
        transitions = {}
        for line in lines[4:]:
            from_state, char, *to_states = [c for c in re.split(r'[,\s]+', line) if c]
            if from_state not in transitions:
                transitions[int(from_state)] = {}
            transitions[int(from_state)][char] = int(to_states)

        print(alphabet)
        print(states)
        print(start_state)
        print(accepting_states)
        print(transitions)
        return DFA(alphabet, states, start_state, accepting_states, transitions)

    # dfa.txt output format:
    #
    # a, b              ->  alphabet
    # q0, q1, q2        ->  states
    # q0                -> start acceptance
    # q2, q1            -> final states
    # q0, a, q1         ->  transitions from 'q0' with 'a' to 'q1'
    # q0, b, q2         -> etc.
    # q1, a, q2
    # q2, b, q0
    @staticmethod
    def write_txt(self, file_path):
        with open(file_path, 'w') as file:
            file.write(','.join(self.alphabet) + '\n')
            file.write(','.join(self.states) + '\n')
            file.write(self.start_state + '\n')
            file.write(','.join(self.accepting_states) + '\n')
            print(self.stated_transitions)
            for from_state, transitions in self.stated_transitions.items():
                for char, to_states in transitions.items():
                    file.write(f"{from_state},{char},{to_states}\n")

    # dfa.json output format:
    #
    # {
    #     "states": ["q0", "q1", "q2"],
    #     "alphabet": ["a", "b"],
    #     "start": "q0",
    #     "accepting": ["q2"],
    #     "transitions": {
    #         "q0": {
    #             "a": ["q1"],
    #             "b": ["q2"]
    #         },
    #         "q1": {
    #             "a": ["q2"]
    #         },
    #         "q2": {
    #             "b": ["q0"]
    #         }
    #     }
    # }
    @staticmethod
    def write_json(self, file_path):
        # print(self.stated_transitions)
        states = []
        for state, trans in self.stated_transitions:
            states.append(state)
        with open(file_path, 'w') as file:
            json.dump({
                'alphabet': list(self.alphabet),
                'states': list(states),
                'start': self.start_state,
                'accepting': list(self.accepting_states),
                'transitions': {
                    state: {char: [to_states] for char, to_states in transitions.items()}
                    for state, transitions in self.stated_transitions.items()
                }
            }, file, indent=4
            )