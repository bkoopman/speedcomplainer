#!/usr/bin/env python

import sys
import time
import json 
import random
import threading
from daemon import Daemon
from datetime import datetime
from logger import Logger

shutdownFlag = False
configFile = "./conf.json"

class SpeedRegDaemon(Daemon):
	def run(self):
		global shutdownFlag
		signal.signal(signal.SIGINT, shutdownHandler)
		
		monitor = Monitor()
		while not shutdownFlag:
			try:
				monitor.run()

				for i in range(0, 5):
					if shutdownFlag:
						break
					time.sleep(1)

			except Exception as e:
				print "Error: %s" % e
				sys.exit(1)

class Monitor():
	def __init__(self):
		self.lastSpeedTest = None

	def run(self):
		if not self.lastSpeedTest or (datetime.now() - self.lastSpeedTest).total_seconds() >= 3600:
			self.runSpeedTest()
			self.lastSpeedTest = datetime.now()

	def runSpeedTest(self):
		speedThread = SpeedTest()
		speedThread.start()

class SpeedTest(threading.Thread):
	def __init__(self):
		super(SpeedTest, self).__init__()
		self.config = json.load(open(configFile))
		self.logger = Logger(self.config["log"]["type"], { "filename": self.config["log"]["file"] })

	def run(self):
		speedTestResults = self.doSpeedTest()
		self.logSpeedTestResults(speedTestResults)

	def doSpeedTest(self):
		# run a speed test
		result = os.popen("/usr/bin/speedtest-cli --simple").read()
		if "Cannot" in result:
			return { "date": datetime.now(), "uploadResult": 0, "downloadResult": 0, "ping": 0 }

		# Result:
		# Ping: 7.886 ms
		# Download: 85.08 Mbits/s
		# Upload: 78.11 Mbits/s

		resultSet = result.split("\n")
		pingResult = resultSet[0]
		downloadResult = resultSet[1]
		uploadResult = resultSet[2]

		pingResult = float(pingResult.replace("Ping: ", "").replace(" ms", ""))
		downloadResult = float(downloadResult.replace("Download: ", "").replace(" Mbits/s", ""))
		uploadResult = float(uploadResult.replace("Upload: ", "").replace(" Mbits/s", ""))

		return { "date": datetime.now(), "uploadResult": uploadResult, "downloadResult": downloadResult, "ping": pingResult }

	def logSpeedTestResults(self, speedTestResults):
		self.logger.log([ speedTestResults["date"].strftime("%Y-%m-%d %H:%M:%S"), str(speedTestResults["uploadResult"]), str(speedTestResults["downloadResult"]), str(speedTestResults["ping"]) ])

if __name__ == "__main__":
	daemon = SpeedRegDaemon("/var/run/speedreg.pid")
	if len(sys.argv) == 2:
		if "start" == sys.argv[1]:
			daemon.start()
		elif "stop" == sys.argv[1]:
			daemon.stop()
		elif "restart" == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
			sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
