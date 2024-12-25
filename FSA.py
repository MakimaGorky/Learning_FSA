from graphviz import Digraph

class DFA:
    def __init__(self):
        init_id = 0

        self.states = {init_id: {}}  # Состояния с переходами
        self.start_state = self.states[init_id] # Начальное состояние
        self.accepting_states = {0}  # Набор принимающих состояний
        self.new_state_id = init_id + 1  # Уникальные идентификаторы для новых состояний

    def add_string(self, string, accepted):
        current_state = 0
        for char in string:
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

    def minimize(self):
        # Находим эквивалентные состояния
        equivalence_classes = {state: (state in self.accepting_states) for state in self.states}

        while True:
            new_classes = {}
            class_map = {}
            for state, transitions in self.states.items():
                key = (equivalence_classes[state],
                       tuple((char, equivalence_classes[transitions[char]]) if char in transitions else None
                             for char in sorted(set(equivalence_classes.values()))))
                if key not in class_map:
                    class_map[key] = len(class_map)
                new_classes[state] = class_map[key]

            if new_classes == equivalence_classes:
                break
            equivalence_classes = new_classes

        # Убираем эквивалентные состояния
        new_states = {}
        new_accepting_states = set()
        state_mapping = {state: equivalence_classes[state] for state in self.states}

        for old_state, new_state in state_mapping.items():
            if new_state not in new_states:
                new_states[new_state] = {}

            for char, target_state in self.states[old_state].items():
                new_states[new_state][char] = state_mapping[target_state]

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

