#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 10 03:49:31 2022

@author: yaroslav
"""
import sys
import os

sys.path.append('/content/af2_wrapper')


import warnings
from absl import logging
import tensorflow as tf

warnings.filterwarnings('ignore')
logging.set_verbosity("error")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')