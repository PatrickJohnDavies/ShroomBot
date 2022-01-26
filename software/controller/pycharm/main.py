# 
# Libraries required:
#   sudo pip install Jetson.GPIO
#

from pickle import TRUE
from subprocess import IDLE_PRIORITY_CLASS
import pandas as pd
import zmq
import multiprocessing
import time

import zeroconf 
import socket as Socket
import logging

import CommandProtocol 

from enum import Enum, auto

class State(Enum):
    INITIALIZE = auto()
    IDLE = auto()
    PREPARE = auto()
    GROWING = auto()
    STOP = auto()
    RESTART = auto()

def findPortOfModule(logger, name):
    logger.debug("findPortOfModule: name = " + name)
    port_selected = -1
    r = zeroconf.Zeroconf()
    logger.debug("2. Testing query of service information...")
    service_info = r.get_service_info("_http._tcp.local.", "ZOE._http._tcp.local.")
    logger.debug("   ZOE service: %s" % (service_info))
    logger.debug("3. Testing query of own service...")
    queried_info = r.get_service_info("_http._tcp.local.", name + "._http._tcp.local.")
    if queried_info:
        expected = {'127.0.0.1'}
        bb = {(queried_info.parsed_addresses())[0]}
        assert bb == expected
        logger.debug("   Getting self: %s" % (queried_info,))
        logger.debug("   Query done.")
        port_selected = queried_info.port
    return port_selected

if __name__ == '__main__':
    module_name = "Controller"
    # Create logger for this module
    logger = logging.getLogger(module_name)
    # create formatter
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(log_formatter)
    logger.addHandler(ch)
    # # create file handler and set level to debug
    # log_fullfilename = os.path.join(module_path, 'log.log')
    # file_handler = logging.FileHandler(log_fullfilename, mode='w')
    # ch.setLevel(logging.DEBUG)
    # file_handler.setFormatter(log_formatter)
    # logger.addHandler(file_handler)
    # logger.setLevel(logging.DEBUG)
    # logger.debug('Created logger')

    # Initialize ZeroMQ
    context = zmq.Context()

    # Initialize Machine Vision
    port = findPortOfModule(logger, "MachineVision")
    if port == -1:
        exit
    logger.debug(f'zeromq machine vision pair starting on port {port}')
    mv_socket = context.socket(zmq.PAIR)
    mv_socket.connect(f"tcp://localhost:{port}")
    mv_cp = CommandProtocol(mv_socket)
    
    # Initialize Arm
    port = findPortOfModule(logger, "Arm")
    if port == -1:
        exit
    logger.debug(f'zeromq arm pair starting on port {port}')
    arm_socket = context.socket(zmq.PAIR)
    arm_socket.connect(f"tcp://localhost:{port}")
    arm_cp = CommandProtocol(arm_socket)

    do_run = TRUE
    state = State.INITIALIZE
    while do_run:
        # Receive commands
        command = view_cp.read(zmq.NOBLOCK)

        # Process the command
        if state == State.INITIALIZE:
            logger.debug('Entered State.INITIALIZE')
            state = State.IDLE
        elif state == State.IDLE:
            logger.debug('Entered State.IDLE')
            if command is not None:
                if command['id'] == 'prepare':
                    state = State.PREPARE
        elif state == State.PREPARE:
            logger.debug('Entered State.PREPARE')
            if command is not None:
                if command['id'] == 'grow':
                    state = State.GROWING
        elif state == State.GROWING:
            logger.debug('Entered State.GROWING')
            if command is not None:
                if command['id'] == 'stop':
                    state = State.STOP
            view_cp.write('analyze')
        elif state == State.STOP:
            logger.debug('Entered State.STOP')
            if command is not None:
                if command['id'] == 'stop':
                    state = State.STOP






