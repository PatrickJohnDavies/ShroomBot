import os
import sys
import logging

import tkinter
import tkinter.simpledialog
from tkinter import ttk
import multiprocessing

import requests

# CONTROLLER_HOSTNAME = 'shroombot_controller.local'
CONTROLLER_HOSTNAME = 'cmio0.local'
# CONTROLLER_HOSTNAME = '127.0.0.1'
CONTROLLER_PORT = 8000
# ARM_HOSTNAME = 'shroombot_controller.local'
ARM_HOSTNAME = '127.0.0.1'
ARM_PORT = 8001
# VISION_HOSTNAME = 'WhatIsItsHostname.local?'
VISION_HOSTNAME = '127.0.0.1'
VISION_PORT = 8002
ENVIROMENT_HOSTNAME = 'esp32.local?'
ENVIROMENT_PORT = 8003

class View(multiprocessing.Process):
    logger = None
    state = 'connect'

    def __init__(self):
        multiprocessing.Process.__init__(self)

    def initSystem(self):
        # Create logger for this module
        View.logger = logging.getLogger(__name__)
        # create formatter
        log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(log_formatter)
        View.logger.addHandler(ch)
        ch.setLevel(logging.DEBUG)
        View.logger.setLevel(logging.DEBUG)
        View.logger.debug('Created logger')

        self.project_path = os.path.dirname(os.path.abspath(__file__))

    def run(self):
        self.initSystem()
        self.root = tkinter.Tk()
        self.process()
        self.root.mainloop()
        self.logger.debug(f'Module exiting')
        self.logging.shutdown()

    def process(self):
        self.processState()
        self.root.after(10, self.process)

    def processState(self):
        if self.state == 'connect':
            self.state = 'initialize'
        elif self.state == 'initialize':
            self.initUi(self.root)
            self.state = 'wait'
        elif self.state == 'wait':
            pass
        elif self.state == 'shutdown':
            self.state = 'wait'
        elif self.state == 'disconnected':
            pass

    def doEnable(parent, status):
        child_list = parent.winfo_children()
        if status:
            state = 'enable'
        else:
            state = 'disable'
        for child in child_list:
            child.configure(state=state)

    def initUi(self, root):
        # root.deiconify()
        # ctypes.windll.shcore.SetProcessDpiAwareness(1)
        # width = root.winfo_screenwidth()
        # height = root.winfo_screenheight()
        width = 500
        height = 500
        root.geometry(f'{(width):.0f}x{(height):.0f}')
        s = tkinter.ttk.Style()
        theme_fullfilename = os.path.join(self.project_path, f'libraries/ttk-Breeze/breeze.tcl')
        root.tk.call('source', theme_fullfilename)
        root.title("ShroomBot")
        root.protocol('WM_DELETE_WINDOW', self.onExit)

        # Menu bar
        self.menubar = tkinter.Menu(root)
        root.config(menu=self.menubar)

        file_menu = tkinter.Menu(self.menubar)
        file_menu.add_command(label="Exit", command=self.onExit)
        self.menubar.add_cascade(label="File", menu=file_menu)

        # device_menu = tkinter.Menu(self.menubar)
        # device_menu.add_command(label="Connect", command=self.deviceConnect)
        # self.menubar.add_cascade(label="Device", menu=device_menu)

        # Layout
        root.grid_columnconfigure(0, weight=1)

        # Control frame
        root.grid_rowconfigure(0, weight=1)
        self.control_frame = View.ControlFrame(root)
        self.control_frame.root.grid(row=0, column=0, sticky="nesw")
        # self.doEnable(self.control_frame, False)

        # Data frame
        root.grid_rowconfigure(1, weight=8)
        self.data_frame = View.DataFrame(root)
        self.data_frame.root.grid(row=1, column=0, sticky="nesw")
        # self.doEnable(self.data_frame, False)

        # Video frame
        root.grid_rowconfigure(2, weight=1)
        self.video_frame = View.VideoFrame(root)
        self.video_frame.root.grid(row=2, column=0, sticky="nesw")
        # self.doEnable(self.control_frame, False)

        # status frame
        root.grid_rowconfigure(3, weight=2)
        self.status_frame = View.StatusFrame(root)
        self.status_frame.root.grid(row=3, column=0, sticky="nesw")
        # self.doEnable(self.status_frame, False)

    def onExit(self):
        View.logger.debug('onExit')
        self.state = 'shutdown'

    class ControlFrame():
        def __init__(self, master):
            self.root = tkinter.Frame(master, bg='yellow')
            label = tkinter.Label(self.root, text="control frame")
            label.grid(row=0, column=0)

            startstop_button = tkinter.Button(self.root, text='Start', command=lambda: self.startstopButtonCallback(startstop_button))
            # stop_button['state'] = tkinter.DISABLED
            startstop_button.grid(row=0, column=1)

            lights_button = tkinter.Button(self.root, text='On', command=lambda: self.lightButtonCallback(lights_button))
            lights_button.grid(row=0, column=2)

            fan_button = tkinter.Button(self.root, text='On', command=lambda: self.fanButtonCallback(fan_button))
            fan_button.grid(row=0, column=3)

        def startstopButtonCallback(self, button):
            if button['text'] == 'Start':
                r = requests.get(f'http://{CONTROLLER_HOSTNAME}:{CONTROLLER_PORT}/start')
                button['text'] = 'Stop'
            elif button['text'] == 'Stop':
                r = requests.get(f'http://{CONTROLLER_HOSTNAME}:{CONTROLLER_PORT}/stop')
                button['text'] = 'Start'
            else:
                raise 'Unkown state'

        def lightButtonCallback(self, button):
            if button['text'] == 'On':
                r = requests.get(f'http://{CONTROLLER_HOSTNAME}:{CONTROLLER_PORT}/lights/on')
                button['text'] = 'Off'
            elif button['text'] == 'Off':
                r = requests.get(f'http://{CONTROLLER_HOSTNAME}:{CONTROLLER_PORT}/lights/off')
                button['text'] = 'On'
            else:
                raise 'Unkown state'

        def fanButtonCallback(self, button):
            if button['text'] == 'On':
                r = requests.get(f'http://{CONTROLLER_HOSTNAME}:{CONTROLLER_PORT}/fan/on')
                button['text'] = 'Off'
            elif button['text'] == 'Off':
                r = requests.get(f'http://{CONTROLLER_HOSTNAME}:{CONTROLLER_PORT}/fan/off')
                button['text'] = 'On'
            else:
                raise 'Unkown state'

    class DataFrame():
        def __init__(self, master):
            self.root = tkinter.Frame(master, bg='blue')
            label = tkinter.Label(self.root, text="data frame")
            label.grid(row=0, column=0)
            # fig = Figure()
            # matplotlib.pyplot.draw()
            # self.root.update()
            # self.root.update_idletasks()
            #
            # self.study_plot.clear()
            # self.study_plot.plot(prices['datetime'], study['value'], color='black')

    class VideoFrame():
        def __init__(self, master):
            self.root = tkinter.Frame(master, bg='green')
            label = tkinter.Label(self.root, text="video frame")
            label.grid(row=0, column=0)

    class StatusFrame():
        def __init__(self, master):
            self.root = tkinter.Frame(master, bg='orange')

            is_armed_label = tkinter.Label(self.root, text="uninitialized", bg='red')
            is_armed_label.grid(row=0, column=0)
            # is_armed_label.configure(text="New String")


if __name__ == '__main__':
    view = View()
    view.start()
    view.join()
