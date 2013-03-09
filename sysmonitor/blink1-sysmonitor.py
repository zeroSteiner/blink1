#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (c) 2013, Spencer J. McIntyre
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#  
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following disclaimer
#    in the documentation and/or other materials provided with the
#    distribution.
#  * The name of the author may not be used to endorse or promote products
#    derived from this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#  

import os
import sys
import usb.core
import psutil
import blink1
from time import sleep
from ConfigParser import ConfigParser

COLOR_SETTINGS = { # (percent, color)
	'high'     : (80, 'red'),
	'mid-high' : (60, 'orange'),
	'mid-low'  : (40, 'yellow'),
	'low'      : ( 0, 'green'),
}

def service(mode, interval):
	blink1_device = None
	while True:
		while blink1_device == None:
			try:
				blink1_device = blink1.Blink1()
			except:
				blink1_device = None
		blink1_device.pattern_stop()
		blink1_device.off()

		while True:
			if mode == 'cpu':
				usage_percentage = psutil.cpu_percent(interval = interval)
			elif mode == 'memory':
				sleep(interval)
				usage_percentage = psutil.virtual_memory().percent
			if usage_percentage >= COLOR_SETTINGS['high'][0]:
				color = COLOR_SETTINGS['high'][1]
			elif usage_percentage >= COLOR_SETTINGS['mid-high'][0]:
				color = COLOR_SETTINGS['mid-high'][1]
			elif usage_percentage >= COLOR_SETTINGS['mid-low'][0]:
				color = COLOR_SETTINGS['mid-low'][1]
			else:
				color = COLOR_SETTINGS['low'][1]
			try:
				blink1_device.set_color(color, fade = 0.5)
			except usb.core.USBError:
				blink1_device = None
				break

def main_cli():
	if len(sys.argv) < 2:
		print 'Usage: blink1-sysmonitor [CONFIG]'
		return os.EX_USAGE

	try:
		configfp = open(sys.argv[1], 'r')
	except IOError:
		print 'Could not open config file: ' + sys.argv[1]
		return os.EX_NOPERM

	config = ConfigParser()
	config.readfp(configfp)
	try:
		if config.has_option('core', 'setuid') and config.has_option('core', 'setgid'):
			setuid = config.getint('core', 'setuid')
			setgid = config.getint('core', 'setgid')
		else:
			setuid = None
			setgid = None
		pid_file = config.get('core', 'pid_file')
		mode = config.get('core', 'mode')
		interval = config.getint('core', 'interval')
	except NoOptionError as err:
		print 'Cound not validate option: \'' + err.option + '\' from config file'
		return os.EX_USAGE
	except ValueError as err:
		print 'Invalid option ' + err.message + ' from config file'
		return os.EX_USAGE
	configfp.close()

	mode = mode.lower()
	if not mode in ['cpu', 'memory']:
		print 'Setting mode must be cpu or memory'
		return os.EX_USAGE

	if setuid != None and setgid != None:
		if os.getuid() != 0:
			print 'Can not setuid() when not running as root'
			return os.EX_NOPERM
	pid = os.fork()
	if pid:
		pid_file_h = open(pid_file, 'w')
		pid_file_h.write(str(pid))
		return os.EX_OK
	if setuid != None and setgid != None:
		os.setregid(setgid, setgid)
		os.setreuid(setuid, setuid)
	service(mode, interval)
	return os.EX_OK

if __name__ == '__main__':
	sys.exit(main_cli())
