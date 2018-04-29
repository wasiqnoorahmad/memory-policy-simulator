#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lib.processes.process import ProcessQueue

virtual_clock = 0
input_queue = ProcessQueue()
expire_queue = {}
turnaroud_times = {}
outfile = None
