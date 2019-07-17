from octoprint.printer.profile import PrinterProfileManager
from octoprint.settings import settings
from octoprint.plugin import plugin_manager
from octoprint.filemanager.analysis import GcodeAnalysisQueue, AnalysisQueue
from octoprint.filemanager import FileDestinations, storage, FileManager
from octoprint.slicing import SlicingManager
from octoprint.printer.standard import Printer, StateMonitor
from data2json import get_data
import RPi.GPIO as gpio
import time
import os
import glob
import shutil

def init_print(absFilename):
	_settings = settings(init=True)
	pluginManager = plugin_manager(init=True)
	pluginManager.reload_plugins(startup=True, initialize_implementations=False)
	printerProfileManager = PrinterProfileManager()
	analysis_queue_factories = dict(gcode=GcodeAnalysisQueue)
	analysis_queue_hooks = pluginManager.get_hooks("octoprint.filemanager.analysis.factory")

	for name, hook in analysis_queue_hooks.items():
		try:
			additional_factories = hook()
			analysis_queue_factories.update(**additional_factories)
		except:
			print("Error while processing analysis queues from {}".format(name))

	analysisQueue = AnalysisQueue(analysis_queue_factories)

	slicingManager = SlicingManager(_settings.getBaseFolder("slicingProfiles"), printerProfileManager)

	storage_managers = dict()
	storage_managers[FileDestinations.LOCAL] = storage.LocalFileStorage(absFilename)

	fileManager = FileManager(analysisQueue, slicingManager, printerProfileManager,
							  initial_storage_managers=storage_managers)

	printer = Printer(fileManager, analysisQueue, printerProfileManager)

	printer_profile = printerProfileManager.get_default()
	connectionOptions = printer.__class__.get_connection_options()

	baselist = []
	baselist = baselist \
			   + glob.glob("/dev/ttyUSB*") \
			   + glob.glob("/dev/ttyACM*") \
			   + glob.glob("/dev/tty.usb*") \
			   + glob.glob("/dev/cu.*") \
			   + glob.glob("/dev/cuaU*") \
			   + glob.glob("/dev/rfcomm*")

	if len(baselist) == 1:
		port = baselist[0]

	print('Connecting to: %s' % port)

	baudrate = 115200

	printer.connect(port=port, baudrate=baudrate,
					profile=printer_profile["id"] if "id" in printer_profile else "_default")

	return printer

def start_print(printer, Filename, save_path, ftp, ftp_dir):

    is_error = False
    is_done = False
    gpio.output(17, False)
    gpio.output(27, False)
    gpio.output(22, False)

    printAfterLoading = True #connect check
    time.sleep(10)
    printer.select_file(Filename, False, printAfterLoading, 'ksko')
    time.sleep(10)

    is_save = [False] * 22

    while printer.is_printing():
        gpio.output(27,True)
        completion = int(printer.get_current_data()['progress']['completion'])
        step = int(completion/5)
        if completion % 5 == 0 and not is_save[step]:
            is_save[step] = True
            get_data(printer, step, save_path, ftp, ftp_dir)
            time.sleep(1)
        if printer.is_finishing():
            is_done = True
            gpio.output(27,False)
            gpio.output(22,True)
            printer.is_closed_or_error()
            break

    print(is_error, is_done)
    get_data(printer, 20, save_path, ftp, ftp_dir)
	time.sleep(5)
    shutil.rmtree(save_path)
    return is_error, is_done
