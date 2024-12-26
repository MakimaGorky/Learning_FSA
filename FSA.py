from graphviz import Digraph
from itertools import product

class DFA:
    def __init__(self):
        init_id = 0

        self.states = {init_id: {}}  # Состояния с переходами
        self.start_state = self.states[init_id]  # Начальное состояние
        self.accepting_states = {0}  # Набор принимающих состояний
        self.new_state_id = init_id + 1  # Уникальные идентификаторы для новых состояний
        self.alphabet = set()  # Изначально молодой и наивный автомат не знает, какому языку ему придётся научиться

    def add_string(self, string, accepted):
        current_state = 0
        for char in string:
            if char not in self.alphabet:
                self.alphabet.add(char)
            if char not in self.states[current_state]:
                self.states[current_state][char] = self.new_state_id
                self.states[self.new_state_id] = {}
                self.new_state_id += 1
            current_state = self.states[current_state][char]

        if accepted:
            self.accepting_states.add(current_state)
        elif current_state in self.accepting_states:
            self.accepting_states.remove(current_state)

        # self.minimize()

    # totally reliably copied exponentially complex manual algorithm
    # TODO make sure it's a proper algorithm
    def minimize(self):
        # Initial 0-equivalence states
        equivalence_classes = {state: (0 if state in self.accepting_states else 1) for state in self.states}

        round = 1

        while True:
            new_classes = {}
            round_class_map = {}
            # for state, transitions in self.states.items():
            #     equivalence_key = (equivalence_classes[state],
            #            tuple((char, equivalence_classes[transitions[char]]) if char in transitions else None
            #                  for char in sorted(set(equivalence_classes.values()))))
            #     if equivalence_key not in round_class_map:
            #         round_class_map[equivalence_key] = len(round_class_map)
            #     new_classes[state] = round_class_map[equivalence_key]

            for state, transitions in self.states.items():
                cnt = 0
                for cls in equivalence_classes.values():  # say no to 🤜 from collections import Counter 👊
                    cnt += int(cls == equivalence_classes[state])
                if cnt == 1:
                    new_classes[state] = equivalence_classes[state]
                    continue  # ✨✨✨

                equivalence_key = []
                for char_comb in product(sorted(set(self.alphabet)), repeat=round):
                    # 😎 cool guys don't turn around when their code works ... 💥
                    # indefinitely
                    temp_state = state
                    for char in char_comb:
                        if temp_state is not None:
                            temp_state = self.states[temp_state][char] if char in self.states[temp_state] else None
                        # POV: this code can't be lazy 😎 🙂 😐 🙁 😨 🤯 💀 ⚰️
                    equivalence_key.append(temp_state)
                comparable_key = (state in self.accepting_states, tuple(equivalence_key))  # even tuple isn't a lazy function haha 😤

                if comparable_key not in round_class_map:
                    round_class_map[comparable_key] = len(round_class_map)  # coincidentally class index
                new_classes[state] = round_class_map[comparable_key]

            round += 1

            if new_classes == equivalence_classes:
                break
            equivalence_classes = new_classes



        # Uniting equivalent classes
        new_states = {}
        new_accepting_states = set()
        compressed_mapping = {state: equivalence_classes[state] for state in self.states}

        for old_state, new_state in compressed_mapping.items():
            if new_state in new_states:
                continue
            
            new_states[new_state] = {}

            for char, target_state in self.states[old_state].items():
                new_states[new_state][char] = compressed_mapping[target_state]

            if old_state in self.accepting_states:
                new_accepting_states.add(new_state)

        self.states = new_states
        self.accepting_states = new_accepting_states

    def visualize(self):
        dot = Digraph()
        for state, transitions in self.states.items():
            cur_shape = "doublecircle" if state in self.accepting_states else "circle"
            dot.node(str(state), shape=cur_shape)
            if state == self.start_state:
                dot.edge('', str(state))
            for char, target in transitions.items():
                dot.edge(str(state), str(target), label=char)
        return dot

