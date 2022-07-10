#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 02:41:05 2022

@author: yaroslav
"""

import time

# =============================================================================
#
# =============================================================================
def syprogressbar(current_step, all_steps, symbol, operation, start_time):
    """Progressbar to show status of any operation and time from the start.

    Takes current step and number of all steps.
    Also takes symbol for progressbar and name
    of the operation. Work inside the cycles and
    requires the counter of its steps"""
    print("{} {}{} {}{}".format(
        "Progress of",
        operation,
        ":",
        int(current_step/all_steps*100),
        "%"))
    print("{}{}{}{}".format(
        "[",
        int(current_step/all_steps*100)*symbol,
        int((all_steps-current_step)/all_steps*100)*"_",
        "]"))
    print(time_check(start_time))
    
# =============================================================================
#
# =============================================================================

def time_check(start_time):
    """Returns the time from the start of some operation.

    Takes start time point in seconds from the epoch
    beginning, calculates the difference between it and
    the current moment and returns it in hh:mm:ss format."""

    current_time = time.time() - start_time
    return "\nTime from the start:\n{} h {:2} m {:2} s\n".format(
        int(current_time//60//60),
        int(current_time//60%60),
        int(current_time%60))
    
# =============================================================================
#
# =============================================================================

def what_time_is_now():
    """Returns current time in seconds from the epoch beginning."""

    return time.time()

# =============================================================================
#
# =============================================================================