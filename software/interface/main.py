import os
import json
import logging
import tkinter
import tkinter.simpledialog
from tkinter import ttk
import multiprocessing
import requests


class View(multiprocessing.Process):
    # logger = None
    state = 'connect'

    def __init__(self, config):
        multiprocessing.Process.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.config = config

    def initSystem(self):
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
        self.control_frame = View.ControlFrame(root, self.config)
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
        def __init__(self, master, config):
            self.config = config
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
                r = requests.get(f"http://{self.config['controller_hostname']}:{self.config['controller_port']}/start")
                button['text'] = 'Stop'
            elif button['text'] == 'Stop':
                r = requests.get(f"http://{self.config['controller_hostname']}:{self.config['controller_port']}/stop")
                button['text'] = 'Start'
            else:
                raise 'Unkown state'

        def lightButtonCallback(self, button):
            if button['text'] == 'On':
                r = requests.get(f"http://{self.config['controller_hostname']}:{self.config['controller_port']}/lights/on")
                button['text'] = 'Off'
            elif button['text'] == 'Off':
                r = requests.get(f"http://{self.config['controller_hostname']}:{self.config['controller_port']}/lights/off")
                button['text'] = 'On'
            else:
                raise 'Unkown state'

        def fanButtonCallback(self, button):
            if button['text'] == 'On':
                r = requests.get(f"http://{self.config['controller_hostname']}:{self.config['controller_port']}/fan/on")
                button['text'] = 'Off'
            elif button['text'] == 'Off':
                r = requests.get(f"http://{self.config['controller_hostname']}:{self.config['controller_port']}/fan/off")
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
    # Create logger for this module
    logger = logging.getLogger(__name__)
    # create formatter
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(log_formatter)
    logger.addHandler(ch)
    ch.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.debug('Created logger')

    # Load the config file
    module_path = os.path.dirname(os.path.realpath(__file__))
    config_fullfilename = os.path.abspath(os.path.join(module_path, "..", "..", "config.txt"))
    logger.debug(f'Checking for config file at: {config_fullfilename}')
    if os.path.isfile(config_fullfilename):
        json_file = open(config_fullfilename)
        config = json.load(json_file)
        json_file.close()
        logger.debug('Config file found.')
    else:
        logger.debug('No config file found. Creating a default one.')
        json_file = open(config_fullfilename, 'w')
        config = {'controller_hostname': 'raspberrypi.local', 'controller_port': '8000', 'arm_hostname': 'raspberrypi.local',
                  'arm_port': '8001', 'vision_hostname': '127.0.0.1', 'vision_port': '8002',
                  'enviroment_hostname': 'esp32.local', 'enviroment_port': '8003'}
        jstr = json.dumps(config, ensure_ascii=False, indent=4)
        json_file.write(jstr)
        json_file.close()
    logger.debug(f'Config is: {config}')

    view = View(config)
    view.start()
    view.join()
