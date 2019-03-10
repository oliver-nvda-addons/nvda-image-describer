# Image describer
# Author: Oliver Edholm
# Copyright 2019, released under GPL.
# Add-on that gets description of current navigator object based on visual features,
# the computer vision heavy computations are made in the cloud.
import sys
import os
import tempfile
import subprocess
from xml.parsers import expat
from collections import namedtuple
from cStringIO import StringIO
import configobj
import tones
import validate
import wx
import config
import globalPluginHandler
import gui
import api
from logHandler import log
import languageHandler
import addonHandler
addonHandler.initTranslation()
import textInfos.offsets
import ui
from time import sleep
from math import sqrt

import base64
import urllib

PLUGIN_DIR = os.path.dirname(__file__)

# Add bundled copy of PIL to module search path.
sys.path.append(os.path.join(PLUGIN_DIR, "PIL"))
import ImageGrab
import Image
del sys.path[-1]

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self):
		super(globalPluginHandler.GlobalPlugin, self).__init__()
		self.imageDescriberSettingsItem = gui.mainFrame.sysTrayIcon.preferencesMenu.Append(wx.ID_ANY,
			_("Image describer settings..."))
		gui.mainFrame.sysTrayIcon.Bind(
			wx.EVT_MENU, self.onImageDescriberSettings, self.imageDescriberSettingsItem)

	def terminate(self):
		try:
			gui.mainFrame.sysTrayIcon.preferencesMenu.RemoveItem(
				self.imageDescriberSettingsItem)
		except wx.PyDeadObjectError:
			pass

	def onImageDescriberSettings(self, event):
		langs = sorted(supportedLocales)
		curlang = getConfig()['language']
		try:
			select = langs.index(curlang)
		except ValueError:
			select = langs.index('en')
		choices = [languageHandler.getLanguageDescription(locale) or locale for locale in supportedLocales]
		dialog = wx.SingleChoiceDialog(gui.mainFrame, _("Select image description language, other languages than english are more prone to translation errors"), _("Image describer settings"), choices=choices)
		dialog.SetSelection(select)
		gui.mainFrame.prePopup()
		ret = dialog.ShowModal()
		gui.mainFrame.postPopup()
		if ret == wx.ID_OK:
			lang = langs[dialog.GetSelection()]
			getConfig()['language'] = lang
			try:
				getConfig().write()
			except IOError:
				log.error("Error writing ocr configuration", exc_info=True)

	def script_analyzeObject(self, gesture):
		api_url = "https://us-central1-icon-classifier.cloudfunctions.net/function-2/interpret_image?locale=%s&b64=%s"

		ui.message(_("Analyzing navigator object"))
		nav = api.getNavigatorObject()

		if not nav.location:
			ui.message(_("This navigator object is not analyzable"))
			return

		left, top, width, height = nav.location

		img = ImageGrab.grab(bbox=(left, top, left + width, top + height))

		maxArea = 35000
		area = width * height
		if area > maxArea:
			scale = sqrt(float(maxArea) / float(area))
			img = img.resize(
				(int(width * scale), int(height * scale))
			)

		buffer = StringIO()
		img.save(buffer, format="JPEG")
		img_str = base64.b64encode(buffer.getvalue())

		lang = getConfig()['language']

		resp = urllib.urlopen(api_url % (lang, img_str)).read().decode('utf-8')

		ui.message(_('Analysis completed: ') + resp)


	__gestures = {
		"kb:NVDA+Control+I": "analyzeObject",
	}

supportedLocales = [
	"bg",
	"ca",
	"cs",
	"da",
	"de",
	"el",
	"en",
	"es",
	"fi",
	"fr",
	"hu",
	"id",
	"it",
	"ja",
	"ko",
	"lt",
	"lv",
	"nb_r",
	"nl",
	"pl",
	"pt",
	"ro",
	"ru",
	"sk",
	"sl",
	"sr",
	"sv",
	"tg",
	"tr",
	"uk",
	"vi",
	"zh_CN"
]

def getDefaultLanguage():
	lang = languageHandler.getLanguage()

	if lang not in supportedLocales and "_" in lang:
		lang = lang.split("_")[0]
	
	if lang not in supportedLocales:
		lang = "en"

	return lang

_config = None
configspec = StringIO("""
language=string(default={defaultLanguage})
""".format(defaultLanguage=getDefaultLanguage()))
def getConfig():
	global _config
	if not _config:
		path = os.path.join(config.getUserDefaultConfigPath(), "imageDescriber.ini")
		_config = configobj.ConfigObj(path, configspec=configspec)
		val = validate.Validator()
		_config.validate(val)
	return _config