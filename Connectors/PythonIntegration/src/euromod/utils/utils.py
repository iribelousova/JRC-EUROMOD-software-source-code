# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 09:39:30 2024

@author: serruha
"""


def is_iterable(variable):
    try:
        iter(variable)
        return True
    except TypeError:
        return False
