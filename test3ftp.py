#!/usr/bin/env python
from ftplib import FTP
import glob
import os
from monitor import start_print, init_print
import RPi.GPIO as gpio


host = '61.79.105.49'
username = 'ftprint'
password = 'print.123'
ftp = FTP("")

com_name = 'lordpower'
print_number = 'lord_printer'
jobNumber = ''


class connection():
    ftp.connect(host)
    ftp.login(username, password)
    ftp.cwd("./JOBS")

    def __init__(self):
		self.is_error = False
		self.is_done = False
		self.temp_path = '/home/pi/Desktop/print/temp'
		gpio.setmode(gpio.BCM)
		gpio.setup(17, gpio.OUT)  # red
		gpio.setup(27, gpio.OUT)  # green
		gpio.setup(22, gpio.OUT)  # blue
		if not os.path.isdir(self.temp_path):
                    os.mkdir(self.temp_path)
		self.printer = init_print(self.temp_path)

    def ftp_connection(self):
		print(ftp.pwd())
		#print(ftp.nlst())
		ftp.cwd('./'+ com_name + '/' + print_number)
		while True:
			print(ftp.nlst())
			for s in ftp.nlst():
				ftp.cwd(s)
				jobNumber = ftp.pwd()
				current_dir = ftp.pwd()
				if "gcode" in ftp.nlst():
					ftp.cwd("gcode")
					if any("gcode" in s for s in ftp.nlst()):
						try:
							file_name = ftp.nlst()[0]
							print('file_name' + file_name)
							if not os.path.isdir(self.temp_path):
								os.mkdir(self.temp_path)
							temp_file_path = os.path.join(self.temp_path, file_name)
							ftp.retrbinary('RETR {}'.format(file_name), open(temp_file_path, "wb").write)
							ftp.cwd(current_dir)
							ftp.rename(current_dir + '/gcode', current_dir + '/gcode_got')
							save_dir = (current_dir + '/status')
							if "status" not in ftp.nlst():
								ftp.mkd(save_dir)
							#if 'temp' not in ftp.nlst():
							#	ftp.mkd(save_dir)
							self.is_error, self.is_done = start_print(self.printer, file_name, self.temp_path, ftp, save_dir)
							if(self.is_error):
								break
							elif(self.is_done):
								ftp.cwd("..")
								break
						except Exception as ex:
							print("Exception error : ", ex)
							ftp.cwd("..")
							gpio.cleanup()
							break
					else:
						ftp.cwd('..')
						ftp.cwd('..')
				else:
					ftp.cwd('..')


    def ftp_quit(self):
        ftp.quit()
        print('ftp ended')


if __name__ == '__main__':
    c = connection()
    c.ftp_connection()
    c.ftp_quit()
