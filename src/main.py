#!/usr/bin/env python
# -*- coding: utf-8 -*-

from argparse import ArgumentParser, FileType
from lib.processes.process import Process
import conf


def get_parser():
    """
    Returns parser to parse command line arguments with command line argument initialized..

    :return parser: ArgumentParser
    """
    parser = ArgumentParser(description='Memory Management Policy Simulator')
    parser.add_argument('-s', '--size', metavar='N', dest='size', type=int,
                        help='memory size in Kb', required=True)

    parser.add_argument('-w', '--workload', metavar='FILE', dest='workload',
                        type=FileType('r'), help='path of workload file', required=True)

    parser.add_argument('-p', '--policy', metavar='N', choices=range(1, 4),
                        dest='policy', type=int, help='memory management policy \n'
                                                      '1- VSP\n'
                                                      '2- PAG\n'
                                                      '3- SEG\n', required=True)

    parser.add_argument('-o', '--output', metavar='FILE', dest='output',
                        type=FileType('w'), help='path of output report file', required=True)

    opts, _ = parser.parse_known_args()
    if opts.policy == 2:
        parser.add_argument('-f', '--frame', metavar='N', dest='frame', type=int,
                            help='frame size in Kb if policy is PAG', required=True)
    else:
        parser.add_argument('-a', '--fit', metavar='N', choices=range(1, 3),
                            dest='fit', type=int, help='fit algorithm'
                                                       '1- First Fit'
                                                       '2- Best Fit', required=True)
    return parser


def to_process(pid, timeline, address_space):
    """
    Input file define the information about a processes in a certain format.
    to_process parses the format and returns equivalent Process object.

    For example: A sample format is:
    1
    0 1000
    1 400
    A processes object will contains the following:
    Process(id=1, start_time=0, life_time=1000, pages_count=1, pages_sizes=[400])

    :param pid: String
    :param timeline: String
    :param address_space: String
    :return processes: Process
    """

    start_time, life_time = timeline.split(' ')
    pages_count, pages_sizes = address_space.split(' ', maxsplit=1)
    obj = {
        'id': int(pid),
        'start_time': int(start_time),
        'life_time': int(life_time),
        'pages_count': int(pages_count),
        'pages_sizes': list(map(int, pages_sizes.split(' ')))
    }
    return Process(obj)


def load_processes(infile):
    """
    Returns a dictionary of all processes loaded from input file based on the
    virtual time value as the keys and processes as valuesin form the processes object.

    :param infile:
    :return processes: dictionary of all processes e.g. {arrival_time: [Process_1, Process_2]}
    """
    total_process = int(infile.readline())
    processes = {}
    while total_process > 0:
        process = to_process(infile.readline(), infile.readline(), infile.readline())
        infile.readline()

        """
        Update dictionary based on processes start time. If there is any other processes
        starting at the same time, append the new processes into the processes list at that 
        particular time. Otherwise, add another key value pair of time and processes. 
        
        """
        if process.start_time in processes:
            processes[process.start_time].append(process)
        else:
            processes[process.start_time] = [process]

        total_process -= 1
    infile.close()
    return processes


def print_timestamp():
    """
    Prints/Write the current virtual clock time.

    :return:
    """
    print('t=' + str(conf.virtual_clock), end='')
    conf.outfile.write('t=' + str(conf.virtual_clock))


def turnaround_time():
    """
    Calculates and print/write the average turnaround time.
    :return:
    """
    average = 0
    for pid, times in conf.turnaroud_times.items():
        average += times[1]-times[0]
    print('Average Turnaround Time: %.2f' % (average/len(conf.turnaroud_times)))
    conf.outfile.write('Average Turnaround Time: %.2f' % (average/len(conf.turnaroud_times)))


def feed_processes(processes, manager):
    """
    Feeds the loaded processes to the input queue and invokes memory manager
    to load process into memory.

    :param processes: dictionary of time: processes
    :param manager: Memory manager object based on chosen policy.
    :return:
    """
    while (processes or conf.input_queue or conf.expire_queue) and conf.virtual_clock < 100000:
        """
        Need to check if the there is any process that must to be removed 
        from the memory at the current virtual time.
        """
        if conf.virtual_clock in conf.expire_queue:
            print_timestamp()
            manager.remove(*conf.expire_queue[conf.virtual_clock])

        """
        Also need to check if there is any process that has arrived at the
        current time. It must then be loaded into the input queue. 
        """
        if conf.virtual_clock in processes:
            print_timestamp()
            conf.input_queue.enque(*processes[conf.virtual_clock])
            del processes[conf.virtual_clock]

        """
        If we have any process in input queue, invoke the memory manager.
        """
        if conf.input_queue:
            manager.load()

        conf.virtual_clock += 1


def main():
    args = get_parser().parse_args()
    processes = load_processes(args.workload)
    conf.outfile = args.output
    if args.policy == 1:                                              # 1 represents VSP policy
        from lib.memory.managers import VSPMM
        feed_processes(processes, VSPMM(args.size, best_fit=args.fit == 2))
    elif args.policy == 2:                                              # 2 represents PAG policy
        from lib.memory.managers import PAGMM
        feed_processes(processes, PAGMM(args.size, args.frame))
    elif args.policy == 3:                                              # 3 represents SEG policy
        from lib.memory.managers import SEGMM
        feed_processes(processes, SEGMM(args.size, best_fit=args.fit == 2))
    turnaround_time()
    conf.outfile.close()


if __name__ == '__main__':
    main()
