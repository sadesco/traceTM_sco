#!/usr/bin/env python3
import sys
import os
import csv
from tqdm import tqdm  # displaying progress bar
from collections import deque  # queue data structure


def parse_tm_file(filename):
    # open and read the TM file
    with open(filename, 'r') as file:
        lines = file.readlines()

    # extract machine parameters from the file
    machine_name = lines[0].strip().split(',')[0]
    states = list(filter(None, lines[1].strip().split(',')))
    input_symbols = list(filter(None, lines[2].strip().split(',')))
    tape_symbols = list(filter(None, lines[3].strip().split(',')))
    start_state = lines[4].strip().split(',')[0]
    accept_states = list(filter(None, lines[5].strip().split(',')))
    reject_state = lines[6].strip().split(',')[0]

    # parse transition rules from the file
    transitions = {}
    for line in tqdm(lines[7:], desc="Reading TM file..."):
        parts = line.strip().split(',')
        if len(parts) == 3:
            src, read_char, dest = parts
            write_char, move = read_char, 'R'
        else:
            src, read_char, dest, write_char, move = parts
        # organize transitions into a dictionary
        if src not in transitions:
            transitions[src] = {}
        if read_char not in transitions[src]:
            transitions[src][read_char] = []
        transitions[src][read_char].append((dest, write_char, move))

    # return machine configuration
    return {
        'name': machine_name,
        'states': states,
        'input_symbols': input_symbols,
        'tape_symbols': tape_symbols,
        'start_state': start_state,
        'accept_states': accept_states,
        'reject_state': reject_state,
        'transitions': transitions,
    }


def get_transition(tm, tape):
    curr_state = tape['state']
    head = tape['head']

    # if no transition exists, return None
    if head not in tm['transitions'].get(curr_state, {}):
        return None
    else:
        new_tapes = []
        # loop through possible transitions and create new tape 
        for dest, write_char, direction in tm['transitions'][curr_state][head]:
            new_tape = {
                'state': dest,
                'left': tape['left'][:],
                'head': write_char,
                'right': tape['right'][:],
            }

            # move head to the right or left on the tape
            if direction == 'R':  # right
                if len(new_tape['right']) == 0:
                    new_tape['right'] = ['_']  # append blank if at the end
                new_tape['left'].append(new_tape['head'])
                new_tape['head'] = new_tape['right'].pop(0)

            else:  # left
                if len(new_tape['left']) == 0:
                    new_tape['left'] = ['_']  # append blank if at the beginning
                new_tape['right'].insert(0, new_tape['head'])
                new_tape['head'] = new_tape['left'].pop()

            new_tapes.append(new_tape)
        return new_tapes


def bfs_simulation(tm, input_str, max_steps, output_file):
    queue = deque()  # initialize the queue for BFS
    tape = {
        'state': tm['start_state'],
        'left': [],
        'head': input_str[0] if input_str else '_',
        'right': list(input_str[1:]),
    }
    queue.append((tape, 0, [tape]))  # add initial tape 
    visited_depths = {}  # dictionary to track visited configurations 
    steps = 0
    accepted = False

    # perform BFS simulation
    while queue and steps < max_steps:
        current_tape, depth, path = queue.popleft()

        # track visited configurations
        if depth not in visited_depths:
            visited_depths[depth] = []
        visited_depths[depth].append(current_tape)

        # check for acceptance state
        if current_tape['state'] in tm['accept_states']:
            accepted = True
            break

        # skip if rejecting state is encountered
        if current_tape['state'] == tm['reject_state']:
            continue

        # get possible transitions for the current state and head
        transitions = tm['transitions'].get(current_tape['state'], {}).get(current_tape['head'], None)
        if not transitions:
            continue

        # loop through transitions and apply them
        for dest, write, direction in transitions:
            new_tape = {
                'state': dest,
                'left': current_tape['left'][:],
                'head': write,
                'right': current_tape['right'][:],
            }

            # update tape with head movement
            if direction == 'R':
                new_tape['left'].append(new_tape['head'])
                if new_tape['right']:
                    new_tape['head'] = new_tape['right'].pop(0)
                else:
                    new_tape['head'] = '_'
            elif direction == 'L':
                new_tape['right'].insert(0, new_tape['head'])
                if new_tape['left']:
                    new_tape['head'] = new_tape['left'].pop()
                else:
                    new_tape['head'] = '_'

            queue.append((new_tape, depth + 1, path + [new_tape]))  # add new tape configuration to the queue
        steps += 1

    # output the result of the simulation
    output_result(tm, input_str, steps, max_steps, accepted, visited_depths, path if accepted else [], output_file)


def output_result(tm, input_str, steps, max_steps, accepted, visited_depths, path, output_file):
    # print and write out the tree depth and total transition count
    print(f"Depth of the tree: {max(visited_depths.keys(), default=0)}.")
    output_file.write(f"Depth of the tree: {max(visited_depths.keys(), default=0)}.\n")

    print(f"Total transitions: {steps}.")
    output_file.write(f"Total transitions: {steps}.\n")

    # output if the string was accepted
    if accepted:
        print(f"String {input_str} accepted in {len(path) - 1} transitions/steps.")
        output_file.write(f"String {input_str} accepted in {len(path) - 1} transitions/steps.\n")
        # print each tape configuration in the acceptance path
        for tape in path:
            tape_repr = f"{''.join(tape['left'])},{tape['state']},{tape['head']},{''.join(tape['right'])}"
            print(tape_repr)
            output_file.write(f"{tape_repr}\n")
    else:
        # output rejection or exceeded max steps
        if steps < max_steps:
            print(f"String: {input_str} rejected in {max(visited_depths.keys(), default=0)} transitions/steps.")
            output_file.write(f"String: {input_str} rejected in {max(visited_depths.keys(), default=0)} transitions/steps.\n")
        else:
            print(f"Execution stopped after {max_steps} maximum steps limit.")
            output_file.write(f"Execution stopped after {max_steps} maximum steps limit.\n")

def main():
    # get the TM file and parse it
    filename = input("Enter Turing Machine file name: ")
    tm = parse_tm_file(filename)

    # prepare output file
    output_filename = tm['name'].replace(' ', '') + "-output.txt"
    if os.path.exists(output_filename):
        os.remove(output_filename)

    with open(output_filename, 'w') as output_file:
        output_file.write(f"Machine Name: {tm['name']}.\n\n")

        while True:
            # get input string from the user
            user_input = input("Enter input string or type quit to exit: ")
            if user_input == "quit":
                break

            max_steps = int(input("Enter maximum steps/transitions: "))

            print(f"\nMachine Name: {tm['name']}")
            print(f"Input string: {user_input}")
            output_file.write(f"Input string: {user_input}\n")

            # simulate the TM and output results
            bfs_simulation(tm, user_input, max_steps, output_file)
            print()
            output_file.write("\n")


if __name__ == "__main__":
    main()
