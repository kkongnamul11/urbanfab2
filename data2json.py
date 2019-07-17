import picamera
import json
import os
import glob

def get_data(p, iter, savePath, ftp, ftp_dir):
	data = dict()
	image_name = 'image_%02d.jpg'%(iter*5)
	temp = p.get_current_temperatures()
	progress = p.get_current_data()['progress']
	#for s in progress :
    #        print(s)
	data["completion"] = progress["completion"]
	data["printTimeLeft"] = progress["printTimeLeft"]
	data["printTime"] = progress["printTime"]
	#data["estimatedPrintTime"] = progress["estimatedPrintTime"]
	data["Temp"] = temp["tool0"]
	data["Bed_Temp"] = temp["bed"]
	data["Image_name"] = image_name
	if(iter == 20):
    		data["completion"] = 100
			data["printTimeLeft"] = 0
	#data["Image_url"] = os.path.join(ftp_dir, image_name)
	with picamera.PiCamera() as camera:
            camera.capture(os.path.join(savePath, image_name), "jpeg")
        upload(ftp, ftp_dir, os.path.join(savePath, image_name))
	with open(os.path.join(savePath, "data_%02d.json"%(iter*5)), "w") as write_file:
            json.dump(data, write_file)
        upload(ftp, ftp_dir, os.path.join(savePath, "data_%02d.json"%(iter*5)))


def upload(ftp, ftp_dir, file_dir):
    ftp.storbinary('STOR {}'.format(os.path.join(ftp_dir, os.path.basename(file_dir))),
                   open(file_dir, "rb"))
