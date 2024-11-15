#from cryptography.fernet import Fernet
import matplotlib.image as mpimg
import pydirectinput as pydirect
import pyautogui as py
from PIL import Image
#import pandas as pd
import numpy as np
import pytesseract
import pyperclip
#import maskpass
import keyboard
import difflib
import time
import cv2
import os

#####		start of charts

gender = 'unknown'
startingVariables = ['', '', '']

pytesseract.pytesseract.tesseract_cmd = os.getcwd() + '\\info\\Tesseract-OCR\\tesseract.exe'

locationDictionary = {}

def check(caseName, region=(0, 0, 1920, 1080), confidence=0.4, center=False):
	directory = os.getcwd() + '\\info\\charts\\' + 'Images\\'
	if (caseName == "okbtn"):
		confidence = 0.7
	if (center):
		confidence = 0.8
	passes = 0
	try:
		while True:
			try:
				location = py.locateOnScreen(directory + caseName + ".png", confidence=confidence)	#region=region
				location.left
				locationDictionary[caseName] = location
				if (center):
					location = py.center(location)
				return location
			except:
				passes += 1
				if (passes > 30):
					if (caseName == "systemsnegative" or caseName == "increments"):
						print("Error with case: ", caseName)
						return 1
					else:
						pydirect.hotkey('alt', 'tab')
						print("\nProgram terminated due to error: ", caseName)
						#print("\n\nPress enter to close the program.", end = "")
						#maskpass.advpass(prompt="", mask="")
						exit()
	except KeyboardInterrupt:
		print("\nProgram terminated by user.")
		#print("\n\nPress enter to close the program.", end = "")
		#maskpass.advpass(prompt="", mask="")
		exit()

def cv2Processor(picture, floor = 255):
	mask = (picture < [floor, floor, floor]).all(axis=2)
	picture[mask] = [0, 0, 0]
	picture[~mask] = [255, 255, 255]
	return picture

def getAge():
	patientAge = ""
	img_rgb = py.screenshot().convert('RGB')
	# img_rgb = cv2.imread(os.getcwd() + "\\Data\\" + i)
	img_rgb = np.array(img_rgb)
	img_rgb = img_rgb[:, :, ::-1].copy()
	img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

	for template_file, gender in zip(['female.png', 'male.png'], ['F', 'M']):
		try:
			template = cv2.imread(os.path.join(os.getcwd(), 'info', 'charts' , 'images', template_file), 0)
			res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
			threshold = 0.9
			loc = np.where(res >= threshold)
			img_rgb = img_rgb[loc[0][0] + 12:loc[0][0] + 34, loc[1][0] + 20:loc[1][0] + 260, ...]
			patientAge = gender
			break
		except:
			pass
	if (patientAge != ""):
		img_rgb = Image.fromarray(cv2Processor(img_rgb, floor=200))
		shortString = pytesseract.image_to_string(img_rgb)
		shortString = shortString.replace('{', '(').replace('}', ')')
		shortString = shortString[shortString.index('(') + 1:shortString.index(')')]
		shortString = shortString.replace('y', '').replace('S', '5').replace('B', '8')
		patientAge += shortString
	return patientAge

def checkTime(input_string):
    if (int(input_string[:2]) > 23 or int(input_string[2:]) > 59):
        return False
    current_time = time.strftime("%H%M")
    current_hour, current_minute = int(current_time[:2]), int(current_time[2:])
    input_hour, input_minute = int(input_string[:2]), int(input_string[2:])

    if current_hour < input_hour:
        current_hour += 24
    
    timeDifference = (current_hour - input_hour) * 60 + (current_minute - input_minute)
    if (timeDifference <= 120 and timeDifference >= 0):
        return True
    return False

def translate_input_to_range(input_str, max_value=None):
    result = set()
    
    # Split the input by commas
    parts = input_str.split(',')
    
    for part in parts:
        part = part.strip()
        
        if '-' in part:
            start_end = part.split('-')
            start = int(start_end[0]) if start_end[0] else 0
            end = int(start_end[1]) if len(start_end) > 1 and start_end[1] else None
            
            if end is not None:
                result.update(range(start, end + 1))
            elif start is not None and end is None:
                if max_value is not None:
                    result.update(range(start, max_value + 1))
                else:
                    # If no max_value is specified, assume up to some large number (e.g., 10000)
                    result.update(range(start, 10001))
        else:
            result.add((part))
    
    return sorted(result)

def startup():
	templates = os.getcwd() + '\\info\\charts\\' + 'documents\\'
	print("Pressing \"enter\" without an entry to the questions below will start the program. It is recommended to not interact with the computer for approxiately 20 seconds after program start.")
	print("\nTo abort the program:\n1. Close the terminal.\n2. Move cursor to the top left of the screen.\n")

	startingVariables[2] = input("Enter patient's chief complaint: ")
	immediateBreak = False
	if (startingVariables[2] == ""):
		immediateBreak = True
		startingVariables[0] = "0"
		return
	deniesList = [f for f in os.listdir(templates + "denies\\") if os.path.isfile(os.path.join(templates + "denies\\", f))]
	deniesList.insert(0, deniesList.pop(deniesList.index("general.txt")))
	for i in range(len(deniesList)):
		if (i > 9):
			print(str(i) + ". " + deniesList[i][:-4])
		else:
			print(str(i) + ".  " + deniesList[i][:-4])
	print("")
	if (not immediateBreak):
		startingVariables[0] = input("Select the category from the list above (Numbers or names are both valid inputs. The program will begin after this): ")
	if (startingVariables[0] == ""):
		startingVariables[0] = "0"
	pt_denies = translate_input_to_range(startingVariables[0], len(deniesList) - 1)
	submittedList = []
	startingVariables[0] = "The patient denies "
	for i in pt_denies:
		if (isinstance(i, int) or i.isnumeric()):
			submittedList.append(deniesList[int(i)][:-4])
		else:
			submittedList.append(i)
	try:
		for i in submittedList:
			text=(open(templates + 'denies\\' + i + '.txt')).read()
			text = text.replace("Denies ", "")
			text = text.replace(". No other symptoms or modifying factors reported at this time.", "")
			text = text.replace(", and", ",")
			text = text.replace(".", ",")
			startingVariables[0] += text + ", "
	except:
		pass
	return

def charts():
	directory = os.getcwd() + '\\info\\charts\\' + 'Images\\'
	templates = os.getcwd() + '\\info\\charts\\' + 'documents\\'
	dailyVariables = os.getcwd() + '\\variables\\'
	variableTexts = [f for f in os.listdir(templates + 'variables\\') if os.path.isfile(os.path.join(templates + 'variables\\', f))]

	startup()
	print('Flip back to the chart and press "enter" to start the program. Remember to not make interactions with the computer for the next 20 seconds.')
	time.sleep(1)
	while (True):
		if keyboard.is_pressed('enter'):
			break
		time.sleep(0.1)

	startingTime = time.time()

	check("hpi", region=(328, 697, 466, 30))								#hpi header

	#gender reveal

	#provider contact/screening time

	py.moveTo(x=875, y=790)
	py.click()
	check("okbtn")								#date popup
	pydirect.press('enter')
	time.sleep(0.5)
	#check("hpi")								#hpi header

	#hpi

	pydirect.press("tab", presses=2, interval = 0.1)
	pyperclip.copy(startingVariables[2])
	time.sleep(0.1)
	pydirect.hotkey('ctrl', 'v')
	providerName=(open(dailyVariables + 'provider.txt')).read()
	if (providerName != "YIN XIA QIAN, PA-C"):
		startingVariables[2] = startingVariables[2].lower()
	pydirect.press("tab")
	#py.moveTo(x=575, y=900)
	#py.click()

	# time.sleep(0.1) substitution

	ptAge = getAge()
	if (len(ptAge) > 0):
		if (ptAge[0] == 'F'):
			gender = 'female'
			startingVariables[0] = startingVariables[0].replace(", testicular pain, testicular mass", "")
		elif (ptAge[0] == 'M'):
			gender = 'male'
			startingVariables[0] = startingVariables[0].replace(", menorrhagia, amenorrhea, vaginal discharge, vulvodynia, pregnancy, menopause", "")
		startingVariables[1] = ptAge[1:]

	##################################################

	text=(open(dailyVariables + 'hpi.txt')).read()
	for i in variableTexts:
		txtContent = (open(templates + 'variables\\' + i)).read()
		text = text.replace('[' + i.replace(".txt", '') + ']', txtContent)
	if (startingVariables[0] == ""):
		text = text.replace('[denies]', '')
	else:
		startingVariables[0] = startingVariables[0][:-2]
		if (providerName != "Nikolay Loboda, PA-C"):
			startingVariables[0] += ". No other symptoms or modifying factors reported at this time."
		lastIndex = startingVariables[0].rfind(",")
		if (lastIndex != -1):
			startingVariables[0] = startingVariables[0][:lastIndex] + ", and" + startingVariables[0][lastIndex + 1:]
		text = text.replace('[denies]', startingVariables[0])
	if (startingVariables[1] == ""):
		text = text.replace('[age]', '')
	else:
		text = text.replace('[age]', startingVariables[1])
	if (startingVariables[2] == ""):
		text = text.replace('[complaint]', '')
	else:
		text = text.replace('[complaint]', startingVariables[2])
	if (gender == 'female'):
		text = text.replace('fe/male', 'female')
	elif (gender == 'male'):
		text = text.replace('fe/male', 'male')
	pyperclip.copy(text)
	#print(text)
	#pydirect.write(text)
	pydirect.hotkey('ctrl', 'v')
	#time.sleep(1)

	#arrival

	providerText=(open(dailyVariables + 'provider.txt')).read()

	btnLocation = check("bodybtn", center=True, region=(39, 289, 81, 46))
	py.moveTo(x=btnLocation[0], y=btnLocation[1])
	py.click()
	check("arrival", region=(347, 260, 280, 30))							#arrival header
	if (", MD" in providerText):
		py.moveTo(x=665, y=325)
		py.click()
		check("ambulance", region=(558, 294, 210, 64))						#ambulance checkbox
	else:
		py.moveTo(x=450, y=325)					#unknown
		py.click()
		check("ambulatory", region=(349, 294, 199, 63))						#arrival checkbox

	#shift page

	btnLocation = check("arrow", confidence = 0.8, center=True)
	time.sleep(0.1)
	py.moveTo(btnLocation[0], btnLocation[1])
	py.click(clicks=2, interval=0.1)
	time.sleep(0.5)
	# exit()
	check("signaturebtn", region=(34, 918, 131, 46))

	#allergies

	btnLocation = check("allergiesbtn", center=True, region=(35, 348, 124, 47))
	py.moveTo(x=btnLocation[0], y=btnLocation[1])
	py.click()
	check("allergies")							#allergies header
	py.moveTo(x=833, y=273)
	py.click()
	check("checkbox")							#allergies checkbox				

	#home medications

	pydirect.press("tab", presses=3, interval = 0.1)
	pydirect.press("space")

	#immunizations

	pydirect.press("tab", presses=3, interval = 0.1)
	pydirect.press("space")

	#past medical history

	pydirect.press("tab", presses=4, interval = 0.1)
	pydirect.press("space")

	#social history

	pydirect.press("tab", presses=5, interval = 0.1)
	pydirect.press("space")

	#family history

	pydirect.press("tab", presses=6, interval = 0.1)
	pydirect.press("space")
	pydirect.press("tab")
	pydirect.press("space")

	btnLocation = check("familyhxbtn", center=True)
	py.moveTo(x=btnLocation[0], y=btnLocation[1])
	py.click()
	check("familyhx")							#family history header

	#review of systems

	btnLocation = check("rosbtn", center=True, region=(40, 531, 74, 44))
	py.moveTo(x=btnLocation[0], y=btnLocation[1])
	check("ros")								#review of systems header
	py.moveTo(x=398, y=719)
	py.click()
	check("roscheckbox")						#review of systems checkbox

	py.moveTo(x=470, y=666)
	py.click()
	btnLocation = check("systemsnegative", confidence=0.7, region=(452, 243, 546, 22))	#review of systems popup
	if (btnLocation != 1):
		time.sleep(0.5)
		py.moveTo(x=btnLocation[0] + 7, y=btnLocation[1] + 7)
		py.click()
		check("additionalcheckbox", region=(btnLocation[0] - 20, btnLocation[1] - 20, 75, 75))	
		py.moveTo(x=btnLocation[0] + 767, y=btnLocation[1] + 597)
		py.click()
		check("ros")							#review of systems header
	else:
		pydirect.press('enter')
		time.sleep(1)

	#vital signs

	btnLocation = check("vitalsbtn", center=True, region=(33, 560, 142, 46))
	py.moveTo(x=btnLocation[0], y=btnLocation[1])
	py.click()
	check("vitals")								#vital signs header
	py.moveTo(x=827, y=273)
	py.click()
	check("checkbox")							#vital signs checkbox

	vitals = py.screenshot().convert('RGB')
	# mpimg.imsave("vitalSigns.png", imageProcessor(mpimg.imread("vitalSigns.png"), floor = 1))

	# btnLocation = check("painbtn", confidence=0.6)
	# # print(btnLocation)
	# py.moveTo(x=btnLocation[0] + 323, y=btnLocation[1] + 11)
	# py.click()
	# check("pain")								#pain indicator
	# py.moveTo(x=btnLocation[0] + 735, y=btnLocation[1] + 11)
	# py.click()
	# check("numeric")							#numeric checkbox

	# pydirect.press("tab", presses=10, interval = 0.1)
	# pydirect.press("space")

	# pydirect.press("tab", presses=6, interval = 0.1)
	# pydirect.press("space")

	#pulse oximetry

	btnLocation = check("resultsbtn", center=True, region=(34, 553, 142, 117))
	py.moveTo(x=btnLocation[0], y=btnLocation[1])
	py.click()
	check("pulse")								#pulse oximetry header

	py.moveTo(x=507, y=320)
	py.click()
	btnLocation = check("increments", region=(566, 185, 400, 23))		#time popup
	print(btnLocation)
	btnLocation = check("nowbtn", confidence = 0.7)
	btnLocation = (btnLocation[0] - 628, btnLocation[1] + 35, btnLocation[2], btnLocation[3])
	print(btnLocation)

	try:
		py.locateCenterOnScreen(directory + 'timecheck.png', confidence=0.7, region=(btnLocation[0] - 40, btnLocation[1] - 10, 40, 40))
		py.moveTo(x=btnLocation[0] - 22, y=btnLocation[1] + 10)
		py.click()
	except:
		pass

	o2Type = "at RA"

	try:
		# img_rgb = cv2.imread("vitalSigns.png")
		# img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
		# template = cv2.imread(os.getcwd() + '\\numbers\\' + 'O2 Sat.png', 0)
		# res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
		# threshold = 0.7
		# loc = np.where(res >= threshold)
		# img_rgb = img_rgb[loc[0][0] - 3:loc[0][0] + 30, loc[1][0] + 80: loc[1][0] + 500, ...]

		img_rgb = np.array(vitals)
		img_rgb = img_rgb[:, :, ::-1].copy()
		img_rgb = cv2Processor(img_rgb)
		img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
		template = cv2.imread(os.getcwd() + '\\info\\charts' + '\\numbers\\' + 'O2 Sat.png', 0)
		res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
		threshold = 0.7
		loc = np.where(res >= threshold)
		img_rgb = img_rgb[loc[0][0] - 3:loc[0][0] + 28, loc[1][0] + 80: loc[1][0] + 500, ...]
		img_rgb = Image.fromarray(img_rgb)
		o2Sat = pytesseract.image_to_string(img_rgb)
		o2Sat = o2Sat.replace(':', '').replace(' ', '').rstrip()

		# dictionary = numberProcessor(img_rgb)
		# o2Sat = dictionaryProcessor(dictionary)
		if (o2Sat == ""):
			raise Exception
		oxygen = int(o2Sat[0:2])
		oxygenTime = o2Sat[-4:]
		print(o2Sat)
		print(oxygenTime)
		if (oxygen < 80):
			if (oxygen == 10 and o2Sat[2] == '0'):
				oxygen = 100
			else:
				print("Double check oxygen")
				raise Exception

		try:
			template = cv2.imread(os.getcwd() + '\\info\\charts' + '\\numbers\\' + 'oxygen.png', 0)
			img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
			res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
			threshold = 0.7
			loc2 = np.where(res >= threshold)
			img_rgb[loc[0][0] - 3:loc[0][0] + 28, loc2[1][0] + 165: loc2[1][0] + 365, ...]
			o2Type = "on oxygen"
		except:
			pass

		if (checkTime(oxygenTime)):
			oxygenHour = int(oxygenTime[0:2])
			xPosition = btnLocation[0] + 33
			if (oxygenHour > 12 or oxygenHour == 0):
				xPosition += 112
			yPosition = btnLocation[1] + 101
			if (oxygenHour == 0):
				oxygenHour = 24
			if (oxygenHour > 12):
				oxygenHour -= 12
			yPosition += int((oxygenHour - 1) * 55.636)

			py.moveTo(x=xPosition, y=yPosition)
			py.click()
			time.sleep(0.1)

			oxygenMinuteTens = int(oxygenTime[2:3])
			xPosition = btnLocation[0] + 321
			yPosition = btnLocation[1] + 105 + (oxygenMinuteTens * 54)
			py.moveTo(x=xPosition, y=yPosition)
			py.click()
			time.sleep(0.1)

			oxygenMinuteOnes = int(oxygenTime[3:4])
			xPosition = btnLocation[0] + 489
			yPosition = btnLocation[1] + 105 + (oxygenMinuteOnes * 54)
			py.moveTo(x=xPosition, y=yPosition)
			py.click()
			time.sleep(0.1)
			pydirect.press('enter')
		else:
			print("Invalid time")
			time.sleep(0.5)
			pydirect.press("esc")
		check("pulse")

		pydirect.press("tab")
		if (oxygen == 100):
			pyperclip.copy("100")
		else:
			pyperclip.copy(o2Sat[0:2])
		pydirect.hotkey('ctrl', 'v')

		pydirect.press("tab")
		if (o2Type == "on oxygen"):
			pydirect.press("tab")
		pydirect.press("space")
		if (o2Type == "at RA"):
			pydirect.press("tab")
		pydirect.press("tab", presses = 2, interval = 0.1)

		if (oxygen < 90):
			o2Type = "Hypoxic " + o2Type
			pydirect.press("tab")
		pydirect.press("space")
		if (oxygen >= 90):
			o2Type = "Normal " + o2Type
			pydirect.press("tab")
		pydirect.press("tab")

		pyperclip.copy(o2Type)
		time.sleep(0.1)
		pydirect.hotkey('ctrl', 'v')
		pydirect.press("tab", presses = 2, interval = 0.1)
		#(left=601, top=187, width=332, height=19)
		
	except:
		pydirect.press("esc")
		time.sleep(0.5)
		btnLocation = check("pebtn", center=True)
		py.moveTo(x=btnLocation[0] - 15, y=btnLocation[1])
		py.click()
		check("assessment")							#physical exam header
		py.moveTo(x=406, y=386)
		py.click()
		time.sleep(0.5)

	#physical exam

	text=(open(dailyVariables + 'provider.txt')).read()
	if (text != "YIN XIA QIAN, PA-C"):
		text=(open(dailyVariables + 'physical.txt')).read()
		if (gender == "male"):
			text=text.replace(" Pelvic exam deferred.\n", '\n')
		for i in variableTexts:
			txtContent = (open(templates + 'variables\\' + i)).read()
			text = text.replace('[' + i.replace(".txt", '') + ']', txtContent)
		pyperclip.copy(text)
		pydirect.hotkey('ctrl', 'v')
		#time.sleep(1)


	#differential

	"""
	btnLocation = check("other", center=True)
	py.moveTo(x=btnLocation[0], y=btnLocation[1])
	py.click()
	check("differential")						#differential header
	py.moveTo(x=380, y=322)
	py.click()
	time.sleep(0.5)
	text=(open(templates + 'differentials\\' + 'abdomen.txt')).read()
	pyperclip.copy(text)
	pydirect.hotkey('ctrl', 'v')
	time.sleep(1)
	"""

	#ed course
	btnLocation = check("planbtn", center=True, region=(37, 790, 102, 117))
	py.moveTo(x=btnLocation[0], y=btnLocation[1])
	py.click()
	check("mdm", region=(314, 257, 655, 39))								#ed course header
	py.moveTo(x=396, y=370)
	py.click()
	time.sleep(1)
	text=(open(dailyVariables + 'mdm.txt')).read()
	text = text.replace(", HEART Score, PERC Score for PE, PECARN Criteria for Child Head Injury, Well's Criteria for DVT/PE, PORT score for Pneumonia etc", "")
	if (", MD" in providerText):
		text = text.replace("\nI have discussed the patient with Dr. [doctor] and he agrees with the patient's plan of care and disposition.\n", "")
	for i in variableTexts:
		txtContent = (open(templates + 'variables\\' + i)).read()
		text = text.replace('[' + i.replace(".txt", '') + ']', txtContent)
	if (startingVariables[1] == ""):
		text = text.replace('[age]', '')
	else:
		text = text.replace('[age]', startingVariables[1])
	if (startingVariables[2] == ""):
		text = text.replace('[complaint]', '')
	else:
		text = text.replace('[complaint]', startingVariables[2])
	if (gender == 'female'):
		text = text.replace('fe/male', 'female')
	elif (gender == 'male'):
		text = text.replace('fe/male', 'male')
	text = text.replace("[provider]", (open(dailyVariables + "provider.txt")).read())
	pyperclip.copy(text)
	pydirect.hotkey('ctrl', 'v')
	time.sleep(0.5)

	#signature

	btnLocation = check("signaturebtn", center=True, region=(34, 918, 131, 46))
	py.moveTo(x=btnLocation[0], y=btnLocation[1])
	py.click()
	check("signature", region=(348, 264, 225, 31))							#signature header
	py.moveTo(x=1300, y=367)
	py.click()
	time.sleep(1)
	text=(open(dailyVariables + 'provider.txt')).read()
	pyperclip.copy(text)
	pydirect.hotkey('ctrl', 'v')
	time.sleep(0.5)
	# py.moveTo(x=1075, y=525)
	# py.click()
	pydirect.press("tab")
	pydirect.press("space")
	check("okbtn")								#date popup
	pydirect.press('enter')
	time.sleep(0.5)
	# py.moveTo(x=1360, y=525)
	# py.click()
	pydirect.press("tab")
	pydirect.press("space")
	# check("increments", region=(566, 185, 400, 23))							#time popup
	btnLocation = check("nowbtn", confidence = 0.7)
	pydirect.press('enter')
	time.sleep(0.5)

	print(time.time() - startingTime)

#####	end of charts

#####	start of imaging

def getTestName():
	directory = os.getcwd() + "\\info\\mdm\\Images\\"
	img_rgb = py.screenshot().convert('RGB')
	img_rgb = np.array(img_rgb)
	img_rgb = img_rgb[:, :, ::-1].copy()
	img_gray = img_rgb.copy()

	img_gray = cv2.cvtColor(img_gray, cv2.COLOR_BGR2GRAY)
	template = cv2.imread(directory + 'tests\\markers\\' + 'square.png', 0)
	res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
	threshold = 0.86			#0.93 threshold
	loc = np.where(res >= threshold)

	img_rgb = img_rgb[loc[0][0] + 145:loc[0][0] + 185, loc[1][0] + 496:loc[1][0] + 1046, ...]
	img_rgb = Image.fromarray(img_rgb)
	shortString = pytesseract.image_to_string(img_rgb)
	lowerCaseString = shortString.lower()

	if ("radiograph" in lowerCaseString):
		shortString = '0' + shortString
	elif ("sonograph" in lowerCaseString or "doppler" in lowerCaseString or "ultrasound" in lowerCaseString or "duplex" in lowerCaseString):
		shortString = '2' + shortString
	elif ("ct" in lowerCaseString):
		shortString = '1' + shortString
	elif ("fluoroscopy" in lowerCaseString or "xr" in lowerCaseString):
		shortString = '0' + shortString
	elif ("us" in lowerCaseString or "cv" in lowerCaseString):
		shortString = '2' + shortString
	else:
		shortString = '3' + shortString
	shortString = shortString.rstrip()
	# print(shortString)
	return shortString

def imaging():
	directory = os.getcwd() + "\\info\\mdm\\Images\\"

	findingsList = [[], [], [], []]
	impressionList = [[], [], [], []]

	incomingString = pyperclip.paste()
	previousTestName = ""
	previousString = pyperclip.paste()

	#pydirect.hotkey('alt', 'tab')
	print('Copy all imaging results at once before pasting. Results will be fed one at a time after every paste. Press the windows key at any time to end this program.')
	print("Ready to start")

	while True:
		try:
			if keyboard.is_pressed('win'):
				return
				exit()
			if keyboard.is_pressed('v'):
				py.press('capslock')
				time.sleep(0.2)
				py.press('capslock')
				break
			elif (incomingString != pyperclip.paste()):
				currentTime = time.time()
				py.press('capslock')
				testName = getTestName()
				
				#py.screenshot(os.getcwd() + "\\Data\\imaging\\images\\" + str(currentTime) + ".png")
				incomingString = pyperclip.paste()

				if (pyperclip.paste() != previousString or testName.lower() != previousTestName):
					lowercaseString = incomingString.lower()
					startingIndex = lowercaseString.find("findings")
					middleIndex = lowercaseString.find("impression:", startingIndex)
					if (middleIndex - 8 == startingIndex or middleIndex == -1):
						middleIndex = startingIndex
					endingIndex = lowercaseString.find("electronically signed", middleIndex)
					endingIndex = lowercaseString.find('    ', endingIndex)
					if ("chest" in testName.lower() and "xr" in testName.lower() or "radiograph" in testName.lower()):
						findingsList[int(testName[0])].insert(0, incomingString[startingIndex:endingIndex])
						impressionList[int(testName[0])].insert(0, testName[1:] + ": " + incomingString[middleIndex:endingIndex])
					else:
						findingsList[int(testName[0])].append(testName[1:])
						findingsList[int(testName[0])].append(incomingString[startingIndex:endingIndex])
						impressionList[int(testName[0])].append(testName[1:] + ": " + incomingString[middleIndex:endingIndex])
					impressionString = ""
					for i in impressionList:
						for j in i:
							impressionString += j + '\n\n'
					impressionString = impressionString[:-2]
					pyperclip.copy(impressionString)
					previousString = incomingString
					incomingString = impressionString
					previousTestName = testName.lower()
				py.press('capslock')
				print(time.time() - currentTime)
			else:
				pass
			time.sleep(0.1)
		except:
			return
			exit()

	for i in findingsList:
		for j in i:
			pyperclip.copy(j)
			try:
				while True:
					if keyboard.is_pressed('win'):
						return
						exit()
					elif (keyboard.is_pressed('v')):
						py.press('capslock')
						time.sleep(0.2)
						py.press('capslock')
						break
					else:
						pass
			except:
				return
				exit()
	pyperclip.copy("Done")

#####	end of imaging

#####	start of mdm

def search_words(word_list, input_word):
	input_word = input_word.lower()
	for i in range(len(input_word) - 1):
		if input_word[i] == ' ' and input_word[i + 1].isdigit() and "ekg" not in input_word and "chest" not in input_word:
			input_word = input_word[:i]
			break
	lowercase_list_list = [[x.lower() for x in sublist] for sublist in word_list]
	lowercase_list = [item.lower() for sublist in word_list for item in sublist]
	processed_lower_list = []
	for i in lowercase_list:
		stringStart = i.find("%$")
		if (stringStart == -1):
			processed_lower_list.append(i)
		else:
			processed_lower_list.append(i[:stringStart])
	lowercase_list = []
	for i in lowercase_list_list:
		tempList = []
		for j in i:
			if ("%$" in j):
				tempList.append(j[:j.index("%$")])
			else:
				tempList.append(j)
		lowercase_list.append(tempList)
	matches = difflib.get_close_matches(input_word, processed_lower_list, cutoff=0.8)
	for i in range(len(matches)):
		for j in range(len(lowercase_list)):
			if (matches[i] in lowercase_list[j]):
				targetString = lowercase_list_list[j][lowercase_list[j].index(matches[i])]
				if ("%$" in targetString):
					indexOf = targetString.index("%$") + 2
					matches[i] = '_' + str(j) + '_' + word_list[j][lowercase_list_list[j].index(targetString)][indexOf:]
				else:
					matches[i] = '_' + str(j) + '_' + word_list[j][lowercase_list_list[j].index(targetString)]
	if len(matches) == 0:
		if ("xr " in input_word or "ct " in input_word or "us " in input_word or "cv " in input_word):
			return "_1_" + input_word.title().rstrip()
		else:
			return input_word.title().rstrip()
	return matches[0]

def mdm():
	directory = os.getcwd() + '\\info\\mdm' + '\\Images\\'
	# pydirect.hotkey('alt', 'tab')
	print('Press "shift" to read the labs that are currently on the screen. Press "ctrl" to end the program and get the results.')
	print("Ready to start")

	listy = [0]
	listx = [622]

	finalList = [[], [], []]
	optionList = ["labs", "imaging", "treatment"]

	while(True):
		try:
			if keyboard.is_pressed('ctrl'):
				finalString = ""
				finalSet = set()
				for i in range(3):
					finalString += optionList[i].capitalize() + " Ordered: "
					for j in range(len(finalList[i])):
						if (finalList[i][j] not in finalSet):
							finalString += finalList[i][j] + ", "
							finalSet.add(finalList[i][j])
					if (len(finalList[i]) == 0):
						finalString += "None"
					else:
						finalString = finalString[:-2]
					finalString += '\n'
				finalString = finalString[:-1]

				print(finalString)

				pyperclip.copy(finalString)
				break
			elif (keyboard.is_pressed('shift')):
				startTime = time.time()
				screenshot = py.screenshot().convert("RGBA")
				screenshot.save(directory + 'workflow\\' + 'unprocessedTest.png')

				py.press('capslock')
				
				img_rgb = cv2.imread(directory + 'workflow\\' + 'unprocessedTest.png')
				img_rgb = cv2Processor(img_rgb, 255)
				cv2.imwrite(directory + 'workflow\\' + 'processedTest.png', img_rgb)
				img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
				template = cv2.imread(directory + 'tests\\markers\\' + 'Description.png', 0)
				res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
				threshold = 0.86			#0.93 threshold
				loc = np.where(res >= threshold)
				if (len(loc[0]) > 0):
					listy = loc[0].tolist()
					listx = loc[1].tolist()
				else:
					listy = [0]
				picture = mpimg.imread(directory + 'workflow\\' + 'processedTest.png')
				seperation = picture[listy[0]:, listx[0] + 370:listx[0] + 371, ...]
				picture = picture[listy[0]:, listx[0] - 14:listx[0] + 374, ...]
				mpimg.imsave(directory + 'workflow\\' + "seperation.png", seperation)
				mpimg.imsave(directory + 'workflow\\' + "croppedTest.png", picture)

				im = Image.open(directory + 'workflow\\' + "seperation.png")



				# Get the width and height of the image
				width, height = im.size

				# Convert the image pixel data to a NumPy array
				pixel_values = np.array(im.getdata())

				# Find indices where the pixel value matches the specified condition (black with full alpha)

				condition = np.logical_or(
					(pixel_values == [0, 0, 0, 255]).all(axis=1),
					(pixel_values == [0, 0, 0, 0]).all(axis=1)
				)

				matching_indices = np.where(condition)[0]

				# Calculate the differences between consecutive matching indices
				diff = np.diff(matching_indices)

				# Identify breaks in consecutive indices
				breaks = np.where(diff != 1)[0]

				# Split the indices at these breaks
				split_indices = np.split(matching_indices, breaks + 1)

				# Create the new list with the first and last elements of each sublist
				newList = np.array([[group[0], group[-1]] for group in split_indices])

				tempList = []
				temppList = newList.tolist()
				first = False

				for i in range(len(temppList)):
					if ((temppList[i][-1] - temppList[i][0]) < 10):
						tempList.append([temppList[i][0], temppList[i][-1]])
						first = True
					elif (first):
						tempList.append([temppList[i][0], temppList[i][-1]])
						break

				newList = np.array(tempList, dtype=object)

				# Filter groups where the range is less than 10
				# newList = newList[(newList[:, 1] - newList[:, 0]) < 10]

				# Create the final list with pairs of ending and starting indices from consecutive groups
				if len(newList) > 1:
					newList = np.array([[newList[i][1], newList[i + 1][0]] for i in range(len(newList) - 1)])
				else:
					newList = np.empty((0, 2), int)

				newList = newList.tolist()

				sectionList = []

				picture = mpimg.imread(directory + 'workflow\\' + 'croppedTest.png')
				for i in range(3):
					text_file = open(directory + "tests\\" + optionList[i] + ".txt", "r").read()
					unprocessedList = text_file.split('\n')
					for j in range(len(unprocessedList)):
						if '\t' in unprocessedList[j]:
							unprocessedList[j] = unprocessedList[j].replace('\t', '%$', 1)
							unprocessedList[j] = unprocessedList[j].replace('\t', '')
					sectionList.append(unprocessedList)
				penultimateList = []

				titan = cv2.imread(os.getcwd() + '\\info\\mdm' + "\\Images\\tests\\markers\\titan.png")
				titan = cv2.copyMakeBorder(titan, 15, 15, 10, 338,cv2.BORDER_CONSTANT,value=(255, 255, 255))
				img_rgb = cv2.imread(directory + 'workflow\\' + 'croppedTest.png')
				imageStacking = titan.copy()

				for i in newList:
					picture = img_rgb[i[0] + 1:i[1], ...]
					paddedPicture = cv2.copyMakeBorder(picture, 10, 0, 0, 0,cv2.BORDER_CONSTANT,value=(255, 255, 255))
					imageStacking = cv2.vconcat([imageStacking, paddedPicture])
					imageStacking = cv2.vconcat([imageStacking, titan])
				cv2.imwrite(os.getcwd() + '\\info\\mdm' + "\\Images\\workflow\\" + "display" + ".png", imageStacking)
				imageStacking = Image.fromarray(imageStacking)
				text = pytesseract.image_to_string(imageStacking)
				if (text != ""):
					text = text.replace("TITAN", "\t")
					text = text.replace('\n', ' ')
					text = text.replace(' %', '%')
					text = text.replace('\t', '\n')
				penultimateList = text.split('\n')
				for i in penultimateList:
					i = i.strip()
					if (i != ''):
						i = search_words(sectionList, i)
						if (i[0:3] == "_0_"):
							finalList[0].append(i[3:])
						elif (i[0:3] == "_1_"):
							finalList[1].append(i[3:])
						elif (i[0:3] == "_2_"):
							finalList[2].append(i[3:])
						else:
							finalList[2].append(i)

				py.press('capslock')
				print(time.time() - startTime)
			else:
				pass
		
		except KeyboardInterrupt:
			print("\nProgram terminated by user.")
			break

#####	end of mdm

#####	start of labs

def imageProcessor(picture, floor = 1):
	red = picture[..., 0]
	green = picture[..., 1]
	blue = picture[..., 2]
	convertToBlack = ((red < floor) & (green < floor) & (blue < floor))
	picture[convertToBlack] = 0
	convertToWhite = ((red != 0) | (green != 0) | (blue != 0))
	picture[convertToWhite] = 1
	return picture

def numberProcessor(img_rgb, numberChanger = 0.75):
	directory = os.getcwd() + '\\info\\labs' + '\\Images\\'
	img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
	dictionary = {}
	dictionaryTracker = {}
	earlyBreak = False
	for i in range(-6, 10):
		letter = str(i)
		if (i == -6):
			letter = 'TNTC'
		elif (i == -5):
			letter = 'Moderate'
		elif (i == -4):
			letter = '-'
		elif (i == -3):
			letter = '+'
		elif (i == -2):
			letter = 'NEGATIVE'
		elif (i == -1):
			letter = 'POSITIVE'
		template = cv2.imread(directory + '\\tests\\numbers\\' + letter + '.png', 0)
		res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
		threshold = numberChanger
		loc = np.where(res >= threshold)
		lists = loc[1].tolist()
		for j in lists:
			letter = letter.replace('+', 'Positive')
			letter = letter.replace('-', 'Negative')
			try:
				value = dictionaryTracker[j]
				if (value < res[loc[0][lists.index(j)]][loc[1][lists.index(j)]]):
					dictionaryTracker[j] = res[loc[0][lists.index(j)]][loc[1][lists.index(j)]]
					dictionary[j] = letter
			except:
				dictionary[j] = letter
				dictionaryTracker[j] = res[loc[0][lists.index(j)]][loc[1][lists.index(j)]]
			if (not letter.isdigit()):
				earlyBreak = True
				break
		if (earlyBreak):
			break
	#print(dictionary)
	return dictionary
 
def dictionaryProcessor(dictionary):
	keys = sorted(dictionary)
	differences = []
	for i in range(1, len(keys)):
		differences.append(keys[i] - keys[i - 1])
	text = ""
	if ((len(keys) > 0)):
		if (keys[0] > 30):
			return text
		elif (keys[0] > 20):
			text += '<='
		elif (keys[0] > 9):
			text += '<'
		elif (keys[0] > 4):
			text += '-'
	for i in range(len(keys)):
		if (i < len(keys) - 1 and differences[i] > 2 or i == len(keys) - 1):
				text += dictionary.get(keys[i])
				if (text == '0'):
					text += '.'
		if (i < len(keys) - 1):
			if (differences[i] > 30):
				break
			elif (differences[i] > 12 and text[-1] != '.'):		#funky #23
				text += '.'
	if (text.count('.') > 1):
		lastDecimal = text.rindex('.')
		text = text[0: lastDecimal].replace('.', '') + text[lastDecimal:]
	try:
		if (not text.includes('.')):
			return int(text)
		return (float(text))
	except:
		return text

def labs():
	directory = os.getcwd() + '\\info\\labs' + '\\Images\\'
	print('Press "shift" to read the labs that are currently on the screen. Press "ctrl" to end the program and get the results.')
	print("Ready to start")
	finalList = []
	while True:
		if keyboard.is_pressed('ctrl'):
			finalString = ""
			for i in finalList:
				finalString += (i[0] + ': ' + str(i[1]) + ', ')
			print(finalString[:-2])
			pyperclip.copy(finalString[:-2])
			finalList = []
			break
		elif keyboard.is_pressed('shift'):
			startTime = time.time()
			screenshot = py.screenshot()
			screenshot.save(directory + 'workflow\\' + 'patientLabs.png')
			py.press('capslock')
			img_rgb = cv2.imread(directory + 'workflow\\' + 'patientLabs.png')

			img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

			template = cv2.imread(directory + 'tests\\markers\\' + 'Test Description.png', 0)
			res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
			threshold = 0.99
			loc = np.where(res >= threshold)
			listy = loc[0].tolist()
			listx = loc[1].tolist()
			picture = mpimg.imread(directory + 'workflow\\' + 'patientLabs.png')
			picture = picture[listy[0]:, listx[0] - 100:listx[0] + 150, ...]
			mpimg.imsave(directory + 'workflow\\' + 'unprocessedTest.png', picture)

			testImage = mpimg.imread(directory + 'workflow\\' + 'unprocessedTest.png')
			mpimg.imsave(directory + 'workflow\\' + 'processedTest.png', imageProcessor(testImage, floor = 1))

			imageFiles = [f for f in os.listdir(directory + 'tests\\labs') if os.path.isfile(os.path.join(directory + 'tests\\labs', f))]
			
			img_rgb = cv2.imread(directory + 'workflow\\' + 'processedTest.png')
			img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

			dictionary = {}

			for i in imageFiles:
				template = cv2.imread(directory + '\\tests\\labs\\' + i, 0)
				res = cv2.matchTemplate(img_gray,template,cv2.TM_CCOEFF_NORMED)
				threshold = 0.86
				loc = np.where(res >= threshold)
				lists = loc[0].tolist()
				if (len(lists) > 0):
					i = i.replace('.png', '')
					#i = i.replace('~', '*')
					i = i.replace('~', '')
					i = i.replace('_', '/')
					i = i.replace('`', '')
					dictionary[lists[0]] = i
					if (i == "TP"):
						dictionary[lists[0] + 26] = "ALB"
						dictionary[lists[0] + 51] = "ALP"
					if (i == "UROBILI"):
						dictionary[lists[0] + 26] = "BILI"

			keys = sorted(dictionary)

			pageResultList = []
			newKeys = []
			for i in keys:
				#print(dictionary[i])
				picture = mpimg.imread(directory + 'workflow\\' + 'patientLabs.png')
				#953, 35w, 23-24h
				picture = picture[i + 84: i + 108:, listx[0] + 642:listx[0] + 677, ...]
				# plt.imsave(os.getcwd() + '\\Temp\\' + str(i) + 'testResult.png', picture)
				mpimg.imsave(directory + 'workflow\\' + 'unprocessedTestResult.png', picture)

				testImage = mpimg.imread(directory + 'workflow\\' + 'unprocessedTestResult.png')
				mpimg.imsave(directory + 'workflow\\' + 'processedTestResult.png', imageProcessor(testImage, 0.72))

				img_rgb = cv2.imread(directory + 'workflow\\' + 'processedTestResult.png')
				if (img_rgb.min() == 0):
					pageResultList.append(dictionary[i])
					newKeys.append(i)

			labResultList = []
			for i in newKeys:
				#print(dictionary[i])
				picture = mpimg.imread(directory + 'workflow\\' + 'patientLabs.png')
				#953, 35w, 23-24h
				picture = picture[i + 84: i + 108:, listx[0] + 416:listx[0] + 611, ...]
				# plt.imsave(os.getcwd() + '\\Temp\\' + str(i) + 'testResult.png', picture)
				mpimg.imsave(directory + 'workflow\\' + 'unprocessedTestResult.png', picture)
				
				testImage = mpimg.imread(directory + 'workflow\\' + 'unprocessedTestResult.png')
				mpimg.imsave(directory + 'workflow\\' + 'processedTestResult.png', imageProcessor(testImage, floor = 0.69))

				img_rgb = cv2.imread(directory + 'workflow\\' + 'processedTestResult.png')
				newDictionary = numberProcessor(img_rgb, numberChanger = 0.65)
				labResultList.append(dictionaryProcessor(newDictionary))
				#positionCoordinates = textProcessor(text, display, 0)

			for i in range(len(pageResultList)):
				if ([pageResultList[i], labResultList[i]] not in finalList):
					finalList.append([pageResultList[i], labResultList[i]])
			py.press('capslock')
			print(time.time() - startTime)
		else:
			pass

def labsAlt():
	print("Copy and paste the lab results from the patient's reports -> SBAR")
	print("Ready to start")
	imcomingString = pyperclip.paste()
	while True:
		try:
			if keyboard.is_pressed('win'):
				return
			elif (imcomingString != pyperclip.paste()):
				text_file = pyperclip.paste()
				word_list = text_file.split('\n')
				finalList = []
				for i in range(len(word_list)):
					word_list[i] = word_list[i].strip()
					if (word_list[i] != "" and "since:" not in word_list[i]):
						for j in range(len(word_list[i])):
							if (word_list[i][j].isdigit() and not word_list[i][j - 1].isalpha()):
								for k in range(j, len(word_list[i])):
									if (not word_list[i][k].isdigit() and word_list[i][k] != '.' and word_list[i][k] != '+'):
										word_list[i] = word_list[i][0:k]
										break
								break
						lowercase = word_list[i].lower()
						wordSearch = ["positive", "negative", "few", "tntc", "trace-intact", "moderate", "many", "equivocal"]
						for j in wordSearch:
							endingIndex = lowercase.find(j)
							if (endingIndex != -1):
								word_list[i] = word_list[i][:endingIndex + len(j)]
								break
						word_list[i] = word_list[i].replace('*', '')
						endingIndex = word_list[i].rfind(' ')
						if (endingIndex != -1):
							word_list[i] = word_list[i][:endingIndex] + word_list[i][endingIndex:].replace(' ', ": ")
						if ('#' not in word_list[i] and '%' not in word_list[i]):
							finalList.append(word_list[i])
				finalString = ""
				for i in finalList:
					finalString += i + ', '
				finalString = finalString[:-2]
				print(finalString)
				pyperclip.copy(finalString)
				return
			else:
				pass
			time.sleep(0.1)
		except:
			return

#####	end of labs

#####	start of admit

def search_doctors(word_list, input_word):
	matches = difflib.get_close_matches(input_word, word_list)
	for i in range(len(matches)):
		matches[i] = matches[i].capitalize()
		matches[i] = "Dr. " + matches[i]
	return matches

def admit():
	directory = os.getcwd() + '\\info\\mdm\\'
	# Example usage:
	text_file = open(directory + "Admitting Doctor Names.txt", "r").read()
	word_list = text_file.split('\n')

	for i in range(len(word_list)):
		word_list[i] = word_list[i].rstrip()
	print("")
	print(word_list)

	for i in range(len(word_list)):
		word_list[i] = word_list[i].replace("Dr. ", "")
		word_list[i] = word_list[i].lower()

	input_word = input("\nEnter a name to search to the best of your ability. Threshold is currently set at 60%: ")

	input_word = input_word.lower()
	input_word = input_word.replace("dr ", "")
	input_word = input_word.replace("dr. ", "")

	result = search_doctors(word_list, input_word)
	print("Matching names:", result)

#####	end of admit

#####	start of shortcut

def shortcut():
	directory = os.getcwd() + '\\info\\mdm\\shortcuts\\'
	shortcut = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
	for i in shortcut:
		txtContent = (open(directory + i)).read()
		if (i == "1.txt"):
			print("1. Discharge Instructions. Comes in three parts.")
		else:
			print(i.replace(".txt", "") + '.', txtContent)
	optionNumber = ""
	while (True):
		optionNumber = input('\nEnter the option name. Enter "0" to quit the program: ')
		if (optionNumber == '0'):
			return
		elif (optionNumber == '1'):
			text_file = (open(directory + optionNumber + ".txt")).read()
			text_file = text_file.split('\n')
			print("Ready to start")
			for i in range(3):
				pyperclip.copy(text_file[i])
				while True:
					if keyboard.is_pressed('win'):
						return
						exit()
					elif (keyboard.is_pressed('v')):
						py.press('capslock')
						time.sleep(0.2)
						py.press('capslock')
						break
					else:
						pass
			print("Successfully copied all instructions")
		else:
			pyperclip.copy((open(directory + optionNumber + ".txt")).read())
			print("Successfully copied")

#####	end of shortcut

#####	start of overhead

def main():
	print("Welcome to Saving Scribes!\n")
	print('Press "ctrl" + "c" or close this window to end the program at any time:')
	try:
		while (True):
			print('Select from the following options:')
			print("1. Set up a chart")
			print("2. Enter lab results")
			print("3. Read provider's orders")
			print("4. Copy imaging results")
			print("5. Find admitting doctor name")
			print("6. Copy shortcut phrases")

			optionNumber = input("\nEnter a number: ")
			trueToken = True
			if (optionNumber == '1'):
				charts()
			elif (optionNumber == '2'):
				print("Choose method:")
				print("1. Screenshot lab results")
				print("2. Copy lab results from reports")
				newNumber = input("\nEnter a number: ")
				if (newNumber == '1'):
					labs()
				else:
					labsAlt()
			elif (optionNumber == '3'):
				mdm()
			elif (optionNumber == '4'):
				imaging()
			elif (optionNumber == '5'):
				admit()
			elif (optionNumber == '6'):
				shortcut()
			else:
				trueToken = False
				print("\nInvalid option. Please try again.\n\n")
			if (trueToken):
				print("\nExecution Finished\n\n")
	except:
		print("\nExecution Failed\n\n")
		print('This terminal will automatically close in 10 seconds. Press "ctrl" + "c" to terminate immediately.')
		time.sleep(10)

main()

#####	end of overhead