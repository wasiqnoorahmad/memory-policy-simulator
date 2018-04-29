#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from lib.memory.maps import VSPMap, PAGMap, SEGMap
from lib.processes.process import PROCESS_MOVE_TO_MEM, PROCESS_COMPLETES
from math import ceil
import conf


class MemoryManager(object):
    """
    Abstract Memory Manager for Processes
    """
    __metaclass__ = ABCMeta

    def __init__(self, memory_map):
        self.map = memory_map

    def remove(self, *processes):
        """
        Removes the process(es) from memory map and expire queue(conf.expire_queue).
        :param processes:
        :return:
        """
        for process in processes:
            process.log(PROCESS_COMPLETES)
            self.map.delete(process.id)
            MemoryManager.cal_turnarounds(process)
            self.map.print_map()
        del conf.expire_queue[conf.virtual_clock]

    def load(self):
        """
        Walks through the input queue and tries to load processes if any.
        If it loads successfully, it notes the expire time of the process
        so it can be omitted from memory when expires.
        If any process cannot be loaded into the memory it remain there in
        the input queue.
        :return:
        """
        walk = 0
        while walk < conf.input_queue.length():
            process = conf.input_queue.get_process(walk)
            """
            move_to_mem tries to load process into memory and return
            true or false on success or failure respectively.
            """
            if self.move_to_mem(process):
                process.log(PROCESS_MOVE_TO_MEM)
                """
                Remove from input queue
                """
                conf.input_queue.deque(process)
                conf.input_queue.log()
                self.map.print_map()
                """
                Note the expire time
                """
                MemoryManager.expires_at(process)
            else:
                walk += 1

    @classmethod
    def expires_at(cls, process):
        """
        Calculates the termination time of the process and store time in expire queue(conf.expire_queue).
        :param process:
        :return:
        """
        expire_time = conf.virtual_clock + process.life_time
        if expire_time in conf.expire_queue:
            conf.expire_queue[expire_time].append(process)
        else:
            conf.expire_queue[expire_time] = [process]

    @classmethod
    def cal_turnarounds(cls, *processes):
        """
        Calculates the turnaround times for process(es) and store values in turnaround(conf.turnaround_time) dictionary.
        :param processes:
        :return:
        """
        for process in processes:
            conf.turnaroud_times[process.id] = conf.turnaroud_times[process.id] + (conf.virtual_clock,)

    @abstractmethod
    def move_to_mem(self, process):
        """
        It tries to load process into the memory. Finds if there is
        enough space for a process, it allocates the blocks appropriately.
        :param process: Process object
        :return <Bool>: True or False if process loading results a success or failure.
        """
        raise NotImplementedError


class PagedMemoryManager(MemoryManager):
    """
    Abstract Paged based Memory Manager for Processes
    """
    __metaclass__ = ABCMeta

    def __init__(self, memory_map):
        super().__init__(memory_map)

    @abstractmethod
    def move_to_mem(self, process):
        raise NotImplementedError


class SegmentMemoryManager(MemoryManager):
    """
    Abstract Segment based Memory Manager for Processes
    """
    __metaclass__ = ABCMeta

    def __init__(self, memory_map, best_fit=False):
        super().__init__(memory_map)
        self.best_fit = best_fit

    @abstractmethod
    def move_to_mem(self, process):
        raise NotImplementedError


class VSPMM(SegmentMemoryManager):
    def __init__(self, size, best_fit=False):
        super().__init__(VSPMap(size), best_fit)

    def move_to_mem(self, process):
        process_size = sum(process.pages_sizes)
        candidate_holes = self.map.lookup(process_size)
        if candidate_holes:
            if not self.best_fit:
                return self.map.allocate(candidate_holes[0], process_size, process.id)
            else:
                diff = {hole[1] - hole[0]: index for index, hole in enumerate(candidate_holes)}
                min_index = min(diff)
                return self.map.allocate(candidate_holes[diff[min_index]], process_size, process.id)
        return False


class SEGMM(SegmentMemoryManager):
    def __init__(self, size, best_fit=False):
        super().__init__(SEGMap(size), best_fit)

    def move_to_mem(self, process):
        if self.map.is_allocatable(process.pages_sizes):
            for index, segment in enumerate(process.pages_sizes):
                candidate_holes = self.map.lookup(segment)
                if candidate_holes:
                    if not self.best_fit:
                        self.map.allocate(candidate_holes[0], segment, process.id, segment=index)
                    else:
                        diff = {hole[1] - hole[0]: index for index, hole in enumerate(candidate_holes)}
                        min_index = min(diff)
                        self.map.allocate(candidate_holes[diff[min_index]], segment, process.id, segment=index)
            return True
        return False


class PAGMM(MemoryManager):
    def __init__(self, size, frame):
        super().__init__(PAGMap(int(size)))
        self.frame = frame

    def move_to_mem(self, process):
        required_pages = int(ceil(sum(process.pages_sizes) / self.frame))
        if self.map.is_allocatable(required_pages * self.frame):
            for page in range(1, required_pages + 1):
                candidate_holes = self.map.lookup(page)
                if candidate_holes:
                    self.map.allocate(candidate_holes[0], self.frame, process.id, segment=page)
            return True
        return False
