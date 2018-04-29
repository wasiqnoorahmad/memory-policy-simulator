#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from sortedcontainers import SortedList


class MemoryMap(object):
    __metaclass__ = ABCMeta

    def __init__(self, size):
        self.size = size
        self.map = {
            'holes': SortedList([(0, self.size - 1)]),
            'allocks': {}
        }

    def lookup(self, size):
        """
        Given an integer <size>, it finds if there is any hole in the memory
        that can accommodate size many kilobytes.
        :param size:
        :return tuple: Memory hole in tuple (start-address, last-address) form that can store size kilobytes.
        """
        return [hole for hole in self.map['holes'] if hole[1] - hole[0] >= size - 1]

    def allocate(self, blocks, size, key, **extra):
        """
        This function tries to allocate size kilobytes from a memory hole given in blocks.
        It also mark the assigned locations with process ID given in key.
        :param blocks: Tuple returned from lookup method that can be used to allocate size kilobytes.
        :param size: Number of kilobytes to allocate.
        :param key: Process ID to lock memory address against for.
        :param extra: Extra parameter like segment or page that can also represent a block of memory.
        :return Bool: True, if the process has been allocates successfully otherwise False.
        """
        if blocks in self.map['holes']:
            offset = blocks[1] - blocks[0] - size + 1
            self.map['holes'].remove(blocks)

            segments = {}
            if key in self.map['allocks']:
                segments = self.map['allocks'][key]
            if offset == 0:
                segments.update({extra['segment']: blocks})
                self.map['allocks'].update({key: segments})
            else:
                segments.update({extra['segment']: (blocks[0], blocks[0] + size - 1)})
                self.map['allocks'].update({key: segments})
                self.map['holes'].add((blocks[0] + size, blocks[1]))
            return True
        return False

    def merge_blocks(self):
        """
        Produces holes after a process leaves the memory needs to be merged for
        easy maintenance and allocations. Produced gaps can either be contiguous to
        a hole already or it might also be possible that a hole now has been merged
        so therefore the current hole is already inside a merged block. This function
        takes care to both scenarios and merge all the produced holes.
        :return:
        """
        def is_contigous(blocks_i, blocks_j):
            return blocks_i[1] - blocks_j[0] == -1

        def is_inside(blocks_i, blocks_j):
            return blocks_i[0] < blocks_j[0] and blocks_i[1] > blocks_j[1]

        walk = 1
        while walk < len(self.map['holes']):
            if is_contigous(self.map['holes'][walk - 1], self.map['holes'][walk]):
                self.map['holes'][walk - 1] = (self.map['holes'][walk - 1][0], self.map['holes'][walk][1])
                self.map['holes'].remove(self.map['holes'][walk])
            elif is_inside(self.map['holes'][walk], self.map['holes'][walk - 1]):
                self.map['holes'].remove(self.map['holes'][walk])
            else:
                walk += 1

    def delete(self, key):
        """
        Given a process id in key, this function remove the process from memory,
        add the produced holes into the record of holes, and finally merge all the holes.
        :param key: Process ID that need to be removed from memory.
        :return Bool: Return True if the process has been removed or False otherwise.
        """

        if key in self.map['allocks']:
            for blocks in self.map['allocks'][key].values():
                self.map['holes'].add(blocks)
            del self.map['allocks'][key]
            self.merge_blocks()
            return True
        return False

    @abstractmethod
    def print_map(self):
        """
        Prints the whole map.
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    def is_allocatable(self, blocks):
        """
        Given a size of blocks, this function checks if there are sufficient holes
        to accommodate all of the blocks. It actually tells if all the blocks of
        the process can be allocated. If yes, we can proceed with loading the whole
        process.
        :param blocks: Size of required blocks.
        :return: True if the process can be accommodated in the memory.
        """
        raise NotImplementedError


class VSPMap(MemoryMap):
    def __init__(self, size):
        super().__init__(size)

    def allocate(self, blocks, size, key, **kwargs):
        if blocks in self.map['holes']:
            offset = blocks[1] - blocks[0] - size + 1
            self.map['holes'].remove(blocks)
            if offset == 0:
                self.map['allocks'].update({key: blocks})
            else:
                self.map['allocks'].update({key: (blocks[0], blocks[0] + size - 1)})
                self.map['holes'].add((blocks[0] + size, blocks[1]))
            return True
        return False

    def delete(self, key):
        if key in self.map['allocks']:
            self.map['holes'].add(self.map['allocks'][key])
            del self.map['allocks'][key]
            self.merge_blocks()
            return True
        return False

    def print_map(self):
        import conf
        sorted_blocks = SortedList([(values[0], values[1], pid) for pid, values in self.map['allocks'].items()])
        [sorted_blocks.add((hole[0], hole[1])) for hole in self.map['holes']]

        print('\tMemory Map: ', end='')
        conf.outfile.write('\tMemory Map: ')
        for i, block in enumerate(sorted_blocks):
            if len(block) == 2:
                print('\t' + str(block[0]) + '-' + str(block[1]) + ': Hole')
                conf.outfile.write(str(block[0]) + '-' + str(block[1]) + ': Hole\n')
            else:
                print('\t' + str(block[0]) + '-' + str(block[1]) + ': Process ' + str(block[2]))
                conf.outfile.write(str(block[0]) + '-' + str(block[1]) + ': Process ' + str(block[2]) + '\n')
            print(2*'\t', end='')
            conf.outfile.write(2*'\t')
        print()
        conf.outfile.write('\n')

    def is_allocatable(self, blocks):
        return True


class SEGMap(MemoryMap):
    def __init__(self, size):
        super().__init__(size)

    def print_map(self):
        import conf
        sorted_blocks = SortedList([(block[0], block[1], pid, segment)
                                    for pid, values in self.map['allocks'].items()
                                    for segment, block in values.items()])

        [sorted_blocks.add((hole[0], hole[1])) for hole in self.map['holes']]

        print('\tMemory Map: ', end='')
        conf.outfile.write('\tMemory Map: ')
        for i, block in enumerate(sorted_blocks):
            if len(block) == 2:
                print('\t' + str(block[0]) + '-' + str(block[1]) + ': Hole')
                conf.outfile.write(str(block[0]) + '-' + str(block[1]) + ': Hole\n')
            else:
                print('\t' + str(block[0]) + '-' + str(block[1]) + ': Process ' +
                      str(block[2]) + ' Segment: ' + str(block[3]))
                conf.outfile.write(str(block[0]) + '-' + str(block[1]) + ': Process '
                                   + str(block[2]) + ' Segment: ' + str(block[3]) + '\n')
            print(2*'\t', end='')
            conf.outfile.write(2*'\t')
        print()
        conf.outfile.write('\n')

    def is_allocatable(self, blocks):
        free_space = 0
        for i in self.map['holes']:
            diff = i[1] - i[0] + 1
            if diff >= min(blocks):
                free_space += i[1] - i[0] + 1
        return free_space >= sum(blocks)


class PAGMap(MemoryMap):
    def __init__(self, size):
        super().__init__(size)

    def print_map(self):
        import conf
        sorted_blocks = SortedList([(block[0], block[1], pid, segment)
                                    for pid, values in self.map['allocks'].items()
                                    for segment, block in values.items()])

        [sorted_blocks.add((hole[0], hole[1])) for hole in self.map['holes']]

        print('\tMemory Map: ', end='')
        conf.outfile.write('\tMemory Map: ')
        for i, block in enumerate(sorted_blocks):
            if len(block) == 2:
                print('\t' + str(block[0]) + '-' + str(block[1]) + ': Free Frame(s)')
                conf.outfile.write(str(block[0]) + '-' + str(block[1]) + ': Free Frame(s)\n')
            else:
                print('\t' + str(block[0]) + '-' + str(block[1]) + ': Process ' + str(block[2])
                      + ' Page: ' + str(block[3]))
                conf.outfile.write(str(block[0]) + '-' + str(block[1]) + ': Process ' + str(block[2])
                                   + ' Page: ' + str(block[3]) + '\n')
            print(2*'\t', end='')
            conf.outfile.write(2*'\t')
        print()
        conf.outfile.write('\n')

    def is_allocatable(self, blocks):
        free_pages = 0
        for hole in self.map['holes']:
            free_pages += hole[1] - hole[0] + 1
        return free_pages >= blocks
