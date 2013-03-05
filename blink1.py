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

import re
import struct
import usb.core
import usb.util

BLINK1_VENDOR_ID  = 0x27b8
BLINK1_PRODUCT_ID = 0x01ed

RGB_COLORS = {
	'red'    : (0xff, 0x00, 0x00),
	'green'  : (0x00, 0xff, 0x00),
	'blue'   : (0x00, 0x00, 0xff),
	'fuschia': (0xff, 0x00, 0xff),
	'yellow' : (0xff, 0xc0, 0x00),
	'orange' : (0xff, 0x80, 0x00),
	'purple' : (0x80, 0x00, 0x80),
	'cyan'   : (0x00, 0xff, 0xff),
	'white'  : (0xff, 0xff, 0xff),
}

__version__ = '0.1'
__all__ = [ 'Blink1', 'count_devices' ]

class Blink1Error(Exception):
	pass

class Blink1InvalidColor(Blink1Error):
	pass

# from https://github.com/todbot/blink1/blob/master/commandline/blink1-lib.c
# a simple logarithmic -> linear mapping as a sort of gamma correction
# maps from 0-255 to 0-255
def _degamma(n):
	return (((1 << (n / 32)) - 1) + ((1 << (n / 32)) * ((n % 32) + 1) + 15) / 32)

def count_devices():
	return len(usb.core.find(idVendor = BLINK1_VENDOR_ID, idProduct = BLINK1_PRODUCT_ID, find_all = True))

class Blink1(object):
	def __init__(self, clear = True):
		self.dev = usb.core.find(idVendor = BLINK1_VENDOR_ID, idProduct = BLINK1_PRODUCT_ID)
		try:
			self.dev.detach_kernel_driver(0)
		except usb.core.USBError:
			pass
		try:
			self.dev._ctx.managed_claim_interface(self.dev, 0)
		except usb.core.USBError:
			pass
		if clear:
			self.pattern_stop()
			self.off()

	def eeprom_read(self, addr, length):
		data = ''
		for idx in xrange(0, length):
			message = struct.pack('BBBBBBBBB', 1, ord('e'), addr + idx, 0, 0, 0, 0, 0, 0)
			self.send(message)
			bmRequestTypeIn = usb.util.build_request_type(usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)
			response = self.dev.ctrl_transfer(bmRequestTypeIn, 1, (3 << 8) | 1, 0, 8)
			data += chr(response[3])
		return data

	def set_color(self, color, fade = 0.0):
		color = color.lower()
		if color in RGB_COLORS:
			rgb_colors = RGB_COLORS[color]
		elif re.match('^0x[0-9a-f]{6}$', color):
			rgb_colors = tuple(map(ord, color[2:].decode('hex')))
		else:
			raise Blink1InvalidColor()
		self.set_rgb(*rgb_colors, fade = fade)

	def set_rgb(self, red = 0, green = 0, blue = 0, fade = 0.0):
		fade     = (min(fade, 655.35) * 100)
		red      = _degamma(red)
		green    = _degamma(green)
		blue     = _degamma(blue)
		message  = struct.pack('BBBBB', 1, ord('c'), red, green, blue)
		message += struct.pack('>H', fade)
		message += struct.pack('BB', 0, 0)
		self.pattern_stop()
		self.send(message)

	def off(self, fade = 0.0):
		self.set_rgb(red = 0, green = 0, blue = 0, fade = fade)

	def on(self, fade = 0.0):
		self.set_rgb(red = 0xff, green = 0xff, blue = 0xff, fade = fade)

	def pattern_clear(self):
		for idx in xrange(1, 13):
			self.pattern_set(idx, 1, 0, 0, 0)

	def pattern_set(self, idx, duration, red = 0, green = 0, blue = 0):
		duration = (min(duration, 655.35) * 100)
		message  = struct.pack('BBBBB', 1, ord('P'), red, green, blue)
		message += struct.pack('>H', duration)
		message += struct.pack('BB', idx, 0)
		self.send(message)

	def pattern_start(self):
		message = struct.pack('BBBBBBBBB', 1, ord('p'), 1, 0, 0, 0, 0, 0, 0)
		self.send(message)

	def pattern_stop(self):
		message = struct.pack('BBBBBBBBB', 1, ord('p'), 0, 0, 0, 0, 0, 0, 0)
		self.send(message)

	def send(self, data):
		reqType = (usb.TYPE_CLASS | usb.RECIP_INTERFACE | usb.ENDPOINT_OUT)
		req = ((3 << 8) | 1)
		self.dev.ctrl_transfer(reqType, req, 0, 0, data)
		return

	@property
	def version(self):
		message = struct.pack('BBBBBBBBB', 1, ord('v'), 0, 0, 0, 0, 0, 0, 0)
		self.send(message)
		bmRequestTypeIn = usb.util.build_request_type(usb.util.CTRL_IN, usb.util.CTRL_TYPE_CLASS, usb.util.CTRL_RECIPIENT_INTERFACE)
		version_raw = self.dev.ctrl_transfer(bmRequestTypeIn, 1, (3 << 8) | 1, 0, 8)
		version = chr(version_raw[3]) + '.' + chr(version_raw[4])
		return version

if __name__ == '__main__':
	from argparse import ArgumentParser
	parser = ArgumentParser(description = 'blink(1) RGB LED', conflict_handler = 'resolve')
	parser.add_argument('-v', '--version', action = 'version', version = parser.prog + ' Version: ' + __version__)
	action_parser = parser.add_mutually_exclusive_group(required = True)
	action_parser.add_argument('-o', '--off', dest = 'turn_off', action = 'store_true', help = 'turn the LED off')
	action_parser.add_argument('-c', '--color', dest = 'color', action = 'store', help = 'set the LED color')
	arguments = parser.parse_args()
	
	blink1_device = Blink1(clear = False)
	if arguments.turn_off:
		blink1_device.off()
	elif arguments.color:
		blink1_device.set_color(arguments.color)
