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

__version__ = '0.2'

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
	from argparse import ArgumentParser
	parser = ArgumentParser(description = 'blink(1) System Monitor', conflict_handler = 'resolve')
	parser.add_argument('-v', '--version', action = 'version', version = parser.prog + ' Version: ' + __version__)
	parser.add_argument('-i', '--interval', dest = 'interval', action = 'store', type = float, default = 2.0, help = 'refresh interval')
	parser.add_argument('-m', '--mode', dest = 'mode', action = 'store', choices = ['cpu', 'mem'], default = 'cpu', help = 'monitor mode') 
	arguments = parser.parse_args()

	mode = arguments.mode
	interval = arguments.interval
	del parser, arguments

	service(mode, interval)
	return os.EX_OK

if __name__ == '__main__':
	sys.exit(main_cli())
