#!/usr/bin/env python

import os
import sys
import time
import logging
from simpledaemon import SimpleDaemon
from datetime import datetime

logFile = "speedresults.csv"

class SpeedRegDaemon(SimpleDaemon):
	def run(self):
		logging.basicConfig(filename=logFile, level=logging.INFO, format="%(message)s")
		
		while True:
			results = self.doSpeedTest()
			logging.info(results["date"].strftime("%Y-%m-%d %H:%M:%S") + "," + str(results["uploadResult"]) + "," + str(results["downloadResult"]) + "," + str(results["ping"]))
			# wait an hour and do it again 
			time.sleep(3600)

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

if __name__ == "__main__":
	workingDirectory, fileNameWithExt = os.path.split(os.path.realpath(__file__))
	fileName, fileExt = os.path.splitext(fileNameWithExt)
	logFile = os.path.join(workingDirectory, logFile)
	pidFile = os.path.join(workingDirectory, fileName + ".pid")
	daemon = SpeedRegDaemon(pidFile)
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
