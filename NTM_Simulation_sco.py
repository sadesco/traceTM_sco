import csv
import itertools
import networkx as nx
import matplotlib.pyplot as plt


class NondeterministicTuringMachine:
    def __init__(self, states, tape_alphabet, input_alphabet, transitions, start_state, accept_states, reject_states):
        self.states = states
        self.tape_alphabet = tape_alphabet
        self.input_alphabet = input_alphabet
        self.transitions = transitions  # {(state, symbol): [(next_state, write_symbol, move)]}
        self.start_state = start_state
        self.accept_states = accept_states
        self.reject_states = reject_states

    def simulate(self, tape):
        """
        Simulates the execution of the NTM and builds an execution tree.
        """
        configurations = [(self.start_state, list(tape), 0, 0)]  # [(state, tape, head_position, parent_node_id)]
        execution_tree = nx.DiGraph()
        execution_tree.add_node(0, label=f"{self.start_state}|{''.join(tape)}")
        node_counter = itertools.count(1)

        while configurations:
            current_state, current_tape, head_position, parent_node = configurations.pop()

            # Add current state to the execution tree
            current_node = next(node_counter)
            execution_tree.add_node(current_node, label=f"{current_state}|{''.join(current_tape)}")
            execution_tree.add_edge(parent_node, current_node)

            if current_state in self.accept_states:
                print(f"Accepted: {''.join(current_tape)}")
                execution_tree.nodes[current_node]["label"] += " (Accepted)"
                continue

            if current_state in self.reject_states:
                print(f"Rejected: {''.join(current_tape)}")
                execution_tree.nodes[current_node]["label"] += " (Rejected)"
                continue

            # Check current symbol under the tape head
            current_symbol = current_tape[head_position] if 0 <= head_position < len(current_tape) else '_'

            # Get all possible transitions for the current state and symbol
            transitions = self.transitions.get((current_state, current_symbol), [])
            for next_state, write_symbol, move in transitions:
                new_tape = current_tape[:]
                if 0 <= head_position < len(new_tape):
                    new_tape[head_position] = write_symbol
                else:
                    new_tape.append(write_symbol)

                # Move the tape head
                new_head_position = head_position + (1 if move == 'R' else -1)
                if new_head_position < 0:
                    new_tape.insert(0, '_')
                    new_head_position = 0

                configurations.append((next_state, new_tape, new_head_position, current_node))

        return execution_tree


def visualize_execution_tree(execution_tree):
    """
    Visualizes the execution tree using networkx and matplotlib.
    """
    pos = nx.nx_agraph.graphviz_layout(execution_tree, prog="dot")
    labels = nx.get_node_attributes(execution_tree, "label")
    plt.figure(figsize=(12, 8))
    nx.draw(execution_tree, pos, with_labels=True, labels=labels, node_size=3000, node_color="lightblue", font_size=8)
    plt.show()


def read_ntm_configuration(csv_file):
    """
    Reads the NTM configuration from a CSV file and returns the parsed data.
    """
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        states = set()
        tape_alphabet = set()
        input_alphabet = set()
        transitions = {}
        start_state = None
        accept_states = set()
        reject_states = set()

        for row in reader:
            states.add(row["current_state"])
            tape_alphabet.add(row["read_symbol"])
            tape_alphabet.add(row["write_symbol"])
            input_alphabet.add(row["read_symbol"])
            transitions.setdefault((row["current_state"], row["read_symbol"]), []).append(
                (row["next_state"], row["write_symbol"], row["move"])
            )

            if row["start_state"].lower() == "true":
                start_state = row["current_state"]
            if row["accept_state"].lower() == "true":
                accept_states.add(row["current_state"])
            if row["reject_state"].lower() == "true":
                reject_states.add(row["current_state"])

    return states, tape_alphabet, input_alphabet, transitions, start_state, accept_states, reject_states


# Example Usage
if __name__ == "__main__":
    # Read NTM configuration from a CSV file
    csv_file = "ntm_configuration.csv"  # Replace with the path to your .csv file
    states, tape_alphabet, input_alphabet, transitions, start_state, accept_states, reject_states = read_ntm_configuration(csv_file)

    # Create an NTM instance
    ntm = NondeterministicTuringMachine(
        states, tape_alphabet, input_alphabet, transitions, start_state, accept_states, reject_states
    )

    # Simulate the NTM on a given input tape
    input_tape = "1101"  # Replace with your input tape
    execution_tree = ntm.simulate(input_tape)

    # Visualize the execution tree
    visualize_execution_tree(execution_tree)
