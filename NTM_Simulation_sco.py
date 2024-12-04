import sys

def read_tm_file(file):
    with open(file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Extract information from the file
    name_machine = lines[0]  # Name of the machine
    states = lines[1].split(",")  # States
    input_alphabet = lines[2].split(",")  # Input alphabet
    tape_alphabet = lines[3].split(",")  # Tape alphabet
    start_state = lines[4]  # Start state
    accept_state = lines[5]  # Accept state
    reject_state = lines[6]  # Reject state
    transitions = {}

    # Parse transition rules
    for line in lines[7:]:
        parts = line.split(",")
        if len(parts) == 5:
            curr, read, next_state, write, direction = map(str.strip, parts)
            if (curr, read) not in transitions:
                transitions[(curr, read)] = []
            transitions[(curr, read)].append((next_state, write, direction))

    return name_machine, start_state, accept_state, reject_state, transitions

def apply_move(left, right, write_char, direction):
    """Applies the move operation to the tape."""
    if right:  # Write on the current position
        right = write_char + right[1:]
    else:  # If the right side is empty, extend the tape with a blank
        right = write_char

    if direction == "R":
        if right:  # Move right
            left += right[0]
            right = right[1:] if len(right) > 1 else "_"
        else:  # If the right side is empty, extend the tape
            left += "_"
    elif direction == "L":
        if left:  # Move left
            right = left[-1] + right
            left = left[:-1]
        else:  # If the left side is empty, extend the tape
            right = "_" + right

    return left, right


def bfs_exp(start_state, accept_state, reject_state, transitions, input, max_step=1000):
    """Performs BFS to simulate the Turing Machine."""
    tree = [[("", start_state, input)]]
    parent = {}
    total_transitions = 0

    for depth in range(max_step):
        if not tree[depth]:
            return False, depth, total_transitions, []
        tree.append([])

        for config in tree[depth]:
            left, state, right = config

            # Check for acceptance
            if state == accept_state:
                path = get_path(config, parent)
                return True, depth, total_transitions, path

            # Skip rejection state
            if state == reject_state:
                continue

            curr_char = right[0] if right else "_"
            moves = transitions.get((state, curr_char), [])

            # If no valid moves, transition to reject state
            if not moves:
                next_config = (left, reject_state, right)
                tree[depth + 1].append(next_config)
                parent[next_config] = config
                total_transitions += 1
                continue

            # Process valid moves
            for next_state, write_char, direction in moves:
                new_left, new_right = apply_move(left, right, write_char, direction)
                next_config = (new_left, next_state, new_right)
                tree[depth + 1].append(next_config)
                parent[next_config] = config
                total_transitions += 1

    return False, max_step, total_transitions, []

def get_path(config, parent):
    """Retrieves the path from the initial state to the current configuration."""
    path = [config]
    while config in parent:
        config = parent[config]
        path.append(config)
    return list(reversed(path))

def main():
    """Main function to run the Turing Machine simulator."""
    if len(sys.argv) != 3:
        print("Usage: python turing_machine.py <tm_file> <input_string>")
        sys.exit(1)

    file = sys.argv[1]
    input = sys.argv[2]

    try:
        name_machine, start_state, accept_state, reject_state, transitions = read_tm_file(file)
    except Exception as e:
        print(f"Error reading TM file: {e}")
        sys.exit(1)

    accepted, steps, total_transitions, path = bfs_exp(start_state, accept_state, reject_state, transitions, input)

    print(f"Machine: {name_machine}")
    print(f"Input: {input}")
    print(f"Depth: {steps}")
    print(f"Total transitions: {total_transitions}")

    if accepted:
        print(f"\nString accepted in {steps} steps")
        print("Accepting path:")
        for left, state, right in path:
            tape = left + (right if right != "_" else "")
            print(f"State: {state}, Tape: {tape}")
    else:
        print(f"\nString rejected in {steps} steps")

if __name__ == "__main__":
    main()
