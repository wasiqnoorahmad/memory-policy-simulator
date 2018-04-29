#!/usr/bin/env python
# -*- coding: utf-8 -*-


PROCESS_ARRIVE = 1
PROCESS_MOVE_TO_MEM = 2
PROCESS_COMPLETES = 3


class Process(object):
    def __init__(self, initial_data):
        for key in initial_data:
            setattr(self, key, initial_data[key])

    def log(self, status=1):
        """
        A process can be either be in one of the states of waiting, running or removed.
        This functions prints the status of the process based of it status code given
        in status argument. Possible values are 1,2,3

        :param status: int value to represent the mode of the process.
        :return:
        """
        import conf
        if status == 1:
            print('\tProcess ' + str(self.id) + ' arrives')
            conf.outfile.write('\tProcess ' + str(self.id) + ' arrives\n')
        elif status == 2:
            print('\tMM moves Process ' + str(self.id) + ' to memory')
            conf.outfile.write('\tMM moves Process ' + str(self.id) + ' to memory\n')
        elif status == 3:
            print('\tProcess ' + str(self.id) + ' completes')
            conf.outfile.write('\tProcess ' + str(self.id) + ' completes\n')


class ProcessQueue(object):
    def __init__(self):
        self.queue = []

    def enque(self, *processes):
        import conf
        for process in processes:
            self.queue.append(process)
            conf.turnaroud_times.update({process.id: (conf.virtual_clock,)})
            process.log()
            self.log()

    def deque(self, *processes):
        for process in processes:
            self.queue.remove(process)

    def length(self):
        return len(self.queue)

    def get_process(self, index):
        return self.queue[index]

    def log(self):
        import conf
        print('\tInput Queue:' + str([pid.id for pid in self.queue]))
        conf.outfile.write('\tInput Queue:' + str([pid.id for pid in self.queue]) + '\n')
