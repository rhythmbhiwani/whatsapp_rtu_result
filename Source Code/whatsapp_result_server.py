from selenium import webdriver
import re
import random
import imgkit
import os
import wget
import platform
import json
import sqlite3
from sqlite3 import Error
from time import sleep
from datetime import datetime
from zipfile import ZipFile
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

dbconnection=sqlite3.connect('studentdata.db')
cursorobj=dbconnection.cursor()
currentworkingdirectory = os.getcwd()
currentworkingdirectorywithfslash = currentworkingdirectory.replace('\\','/')
Link = "https://web.whatsapp.com/" #Link for whatsapp web
roll_no_pattern = re.compile('\d{2}[A-Z]{5}\d+', re.I) #Roll number pattern
examname = None
examcode = None
examurl = None

with open('helpingdata.json') as data:
  helpingdata = json.load(data)

def insert2db(rollno, res):
	sql="SELECT * from student where rollno='{}' and examid='{}';".format(rollno.upper(),examcode)
	cursorobj.execute(sql)
	record = cursorobj.fetchone()
	if record==None:
		qry="INSERT INTO student (rollno, examid, res) VALUES ('{}','{}',{});".format(rollno.upper(),examcode,res)
		cursorobj.execute(qry)
		dbconnection.commit()

def showpercentage(rollno):
    sql="SELECT res from student where rollno='{}' and examid='{}';".format(rollno.upper(),examcode)
    cursorobj.execute(sql)
    record = cursorobj.fetchone()
    if record==None:
    	return False
    return record[0]

#selecting exam name
def selectexamname():
	global examname
	global examcode
	global examurl
	examlist = list(helpingdata['examtitle'].keys())
	count = 0
	for i in examlist:
		count+=1
		print(count,'->',i)
	while True:
		try:
			choice = int(input("Enter index of exam you want to launch server for: "))
			if choice<=0 or choice>count:
				print("Enter number from the above list!")
			else:
				examname = examlist[choice-1]
				examcode = helpingdata['examtitle'][examname][0]
				examurl = helpingdata['examtitle'][examname][2]
				print(examname,"Selected!")
				break
		except Exception as e:
			print('Please enter correct value!')
#calling function
selectexamname()


#Check if chromedriver is present or not
def downloadchromedriver(operatingsystem):
	url = helpingdata['chromedriverlink'][operatingsystem]
	if operatingsystem=='linux':
		if not os.path.exists("chromedriver/chromedriverlinux"):
			print("Chromedriver not found downloading....")
			wget.download(url, 'chromedriver/chromedriver_linux64.zip')
			os.chdir('chromedriver')
			with ZipFile(os.path.abspath("chromedriver_linux64.zip"), 'r') as zipObj:
				zipObj.extractall()
			os.rename('chromedriver','chromedriverlinux')
			os.system('chmod +x chromedriverlinux')
			os.remove('chromedriver_linux64.zip')
			os.chdir('..')
			os.system('sudo apt-get install wkhtmltopdf -y')
	elif operatingsystem=='windows':
		if not os.path.exists("chromedriver/chromedriver.exe"):
			print("Chromedriver not found downloading....")
			wget.download(url, 'chromedriver/chromedriver_win32.zip')
			os.chdir('chromedriver')
			with ZipFile(os.path.abspath("chromedriver_win32.zip"), 'r') as zipObj:
				zipObj.extractall()
			os.remove('chromedriver_win32.zip')
			os.chdir('..')


myos = platform.system().lower()
if 'linux' in myos:
	slash = '/'
	currentworkingdirectory = currentworkingdirectory.replace('\\','/')
	cdname = 'chromedriverlinux'
	downloadchromedriver('linux')
elif 'windows' in myos:
	slash = '\\'
	cdname = 'chromedriver.exe'
	downloadchromedriver('windows')
#Get webdriver for searching result
result_options = Options()
result_options.add_argument('--headless')
result_options.add_argument('--disable-gpu')
result_options.add_argument('--log-level=3')
driver = webdriver.Chrome('chromedriver'+slash+cdname, options=result_options)
# driver = webdriver.Chrome('chromedriver'+slash+cdname)

#Read blacklist
def readblaklist(rno):
	sql="SELECT * from blacklist where rollno='{}' and examid='{}';".format(rno.upper(),examcode)
	cursorobj.execute(sql)
	record = cursorobj.fetchone()
	if record==None:
		return False
	return True

#Blacklist number
def writeblacklist(rno):
	sql="SELECT * from blacklist where rollno='{}' and examid='{}';".format(rno.upper(),examcode)
	cursorobj.execute(sql)
	record = cursorobj.fetchone()
	if record==None:
		qry="INSERT INTO blacklist (rollno, examid) VALUES ('{}','{}');".format(rno.upper(),examcode)
		cursorobj.execute(qry)
		dbconnection.commit()


#function to save log
def loggerfun(name,rollno,status):
	with open('log.txt','a') as log:
		text = str(datetime.now())[:-7]+"\t"+name+"\t\t"+str(rollno).upper()+"\t"+status+"\t\t"+examcode+"\n"
		print(text)
		log.write(text)

def page_has_loaded(driver):
    page_state = driver.execute_script('return document.readyState;')
    return page_state == 'complete'

#function to get result
def get_result(rollno):
	global examname
	global examcode
	rollno=rollno.upper() #Capitalize roll number
	driver.get(examurl) #load result url

	pagestatus = page_has_loaded(driver)
	while pagestatus!=True:
		pagestatus = page_has_loaded(driver)

	rollnumberinputbox = driver.find_element_by_id("Rollno")

	rollnumberinputbox.send_keys(rollno)

	driver.execute_script("GetResultByRollNo();")
	sleep(2)

	pagestatus = page_has_loaded(driver)
	while pagestatus!=True:
		pagestatus = page_has_loaded(driver)
		
	try:
		#execute JS to extract result
		examname = driver.execute_script('''return document.getElementById("ExamName").value;''')
		res = driver.execute_script('''var divToPrint = document.getElementById('printarea');
	        var htmlToPrint = '' + '<style type="text/css">@page { size: auto;  margin: 0mm; } table th, table td {border:1px solid #000;padding:0.5em;}  </style>';
	        htmlToPrint += divToPrint.outerHTML;
	        return htmlToPrint;''')
		index = res.find('<font face="Verdana" size="2">') + 33
		res = res[:index] + "Result Deliverd by : Rhythm Bhiwani"+ res[index:]
		#replacing image urls
		res = res.replace(re.findall('src=".*"',res)[0].split()[0], 'src="'+'file:///'+currentworkingdirectorywithfslash+'/images/banner2.jpg"')
		res = res.replace('/images/strip.jpg','file:///'+currentworkingdirectorywithfslash+'/images/strip.jpg')
		index = res.find(' Grand Total </b> </font></td><td align="center"><font> <b>')
		total = int(re.findall('\d+|$', res[index:index+100])[0])
		per = (total*100)/float(helpingdata['examtitle'][examname][1])
		insert2db(rollno,per)
		#Convert Result from html to image
		imgkit.from_string(res, 'Results/'+rollno+'_'+examcode+'.jpg')
		return 1 #Return 1 if result saved successfully
	except Exception as e:
		# print(e)
		return 0 #Return 0 if result not found

#function to send result save in location to whatsapp
def send_result(name,filepath,rollno):
	global examname
	user = browser.find_element_by_xpath('//span[@title = "{}"]'.format(name)) #Search user number
	user.click()

	attachment_box = browser.find_element_by_xpath('//div[@title = "Attach"]') #search attach button
	attachment_box.click()

	#find images button
	image_box = browser.find_element_by_xpath('//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
	image_box.send_keys(filepath) #send location of result

	sleep(1)
	msg_box = browser.find_element_by_xpath('//*[@id="app"]/div/div/div[2]/div[2]/span/div/span/div/div/div[2]/div[1]/span/div/div[2]/div/div[3]/div[1]/div[2]') #find text box
	per = "%.2f" %showpercentage(rollno)
	msg_box.send_keys(examname+" [Score: {}%]".format(per)) #Send message to text box

	send_button = browser.find_element_by_xpath('//span[@data-icon="send-light"]') #click send button
	send_button.click()
	#Click on WHO account
	who = browser.find_element_by_xpath('//span[@title = "{}"]'.format("World Health Organization"))
	who.click()

#function to send message if result not found
def send_message(name,msg):
	user = browser.find_element_by_xpath('//span[@title = "{}"]'.format(name)) #find user
	user.click()
	msg_box = browser.find_element_by_class_name('_1Plpp') #find text box
	msg_box.send_keys(msg) #Send message to text box
	button = browser.find_element_by_xpath('//span[@data-icon="send"]') #find send button
	button.click()
	#Click on WHO account
	who = browser.find_element_by_xpath('//span[@title = "{}"]'.format("World Health Organization"))
	who.click()


#Send fail message
def failmsg(name,rno,send_msg = None):
	if send_msg==None:
		send_msg = ['Cannot find result, please check roll number','Looks like roll number is not correct!','Oops, cannot find result, check roll number'][random.randint(0,2)]
	send_message(name,send_msg) #send error message
	loggerfun(name,rno,"FAIL")


#send success message
def successmsg(name,filepath,rno):
	send_result(name,filepath,rno) #send result if already exist
	loggerfun(name,rno,"SUCCESS") #log success


#Loading cookies into chrome for auto login whatsapp
chrome_options = Options()
chrome_options.add_argument('--user-data-dir=./User_Data')
browser = webdriver.Chrome('chromedriver'+slash+cdname, options=chrome_options)
wait = WebDriverWait(browser, 600)
browser.get(Link) #opening whatsapp web

sleep(20)
while True:
	try:
		count = 1
		while True:
			#find all messages
			msg  = str(browser.find_element_by_xpath('//*[@id="pane-side"]/div[1]/div/div/div['+str(count)+']/div/div/div/div[2]').text).split()
			count+=1
			#check for new messages
			if msg[-1].isdigit():
				matched_rollno = list(filter(roll_no_pattern.match, msg)) #check if roll no in message
				if len(matched_rollno)>=1:
					name = " ".join(msg[0:3])
					filepath = currentworkingdirectory+slash+'Results'+slash+matched_rollno[0].upper()+'_'+examcode+'.jpg' #Make user name from mobile number
					if len(matched_rollno[0])!=10:
						send_msg = ['Please enter Roll Number in correct format!','Roll Number incorrect!','Enter Correct Roll Number!'][random.randint(0,2)]
						failmsg(name,matched_rollno[0],send_msg)
						continue
					#check if roll number is in blacklist
					if readblaklist(matched_rollno[0]):
						failmsg(name,matched_rollno[0])
						continue
					#check if result for roll no already saved
					if os.path.exists(filepath):
						successmsg(name,filepath,matched_rollno[0])
						continue
					res = get_result(matched_rollno[0]) #find result if not already saved
					if res:
						#if result found and saved
						successmsg(name,filepath,matched_rollno[0])
					else:
						failmsg(name,matched_rollno[0])
						writeblacklist(matched_rollno[0]) #add rollno to blacklist
	except Exception as e:
		# print(e)
		sleep(1)
