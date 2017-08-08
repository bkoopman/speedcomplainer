#!/usr/bin/env python

import os
import sys
import time
from datetime import datetime
import daemon
from daemon import pidfile
import signal
import threading
import json 
import random
from logger import Logger

shutdownFlag = False
configFile = "./conf.json"

def main(filename, argv):
	print "======================================"
	print " Starting Speed Registration          "
	print "======================================"
	
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
	
	sys.exit()

def shutdownHandler(signo, stack_frame):
	global shutdownFlag
	print "Got shutdown signal (%s: %s)." % (signo, stack_frame)
	shutdownFlag = True

def start_daemon(workingDirectory, fileNameWithExt, scriptName, args):
	fileName, fileExt = os.path.splitext(fileNameWithExt)
	pidFilePath = os.path.join(workingDirectory, fileName + ".pid")
	
	# launch the daemon in its context
	context = daemon.DaemonContext(
		working_directory = workingDirectory,
		umask = 0o002,
		pidfile = pidfile.TimeoutPIDLockFile(pidFilePath),
		signal_map = { signal.SIGTERM: "terminate", signal.SIGHUP: "terminate" },
		stdin = "/dev/null",
		stdout = "/dev/null",
		stderr = "/dev/null",
		)
	
	with context:
		main(scriptName, args)

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
	workingDirectory, fileNameWithExt = os.path.split(os.path.realpath(__file__))
	start_daemon(workingDirectory, fileNameWithExt, __file__, sys.argv[1:])
