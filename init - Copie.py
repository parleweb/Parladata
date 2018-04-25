"""
Parladata
init.py
"""

# IMPORT
import sys
import os
from datetime import datetime
import logging

from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader, TemplateNotFound, TemplateSyntaxError, UndefinedError
import markdown2
import json
import csv
from pprint import pprint


# parladata global string
verPackage = "PARV4"

# parladata package
from .log import logger, loglevel
from .template import PlwTemplate
from .data import PlwData
from .scan import PlwScan


# GLOBAL VARIABLES
# info

WEBMASTER = 'Emmanuel Sandorfi - Recherche et développement python'


# OBJECT PlwInit
#	Use as container for configuration
#	Use as route commands
#
# 	object defined
#		myTemplate (PlwTemplate), myData (PlwData)
#	variables defined
#		stopIfError, noError - route function return
#		static - static output path
#	functions
#		__init__, route, pushstatic
#
class PlwInit(object):
	# INIT
	# SET DEFAULT URLS AND PATH
	def __init__(self, input_path, profile_path, static_path, root_url, fw_url, static_url, template_path, data_path, static_idx_path, home_url, fdebug = 0):


		# set datetime
		self.dtstart = datetime.now()

		# loglevel
		#loglevel(fdebug)

		# replace url
		root_url = root_url.replace('\\', '/')
		fw_url = fw_url.replace('\\', '/')
		static_url = static_url.replace('\\', '/')
		home_url = home_url.replace('\\', '/')



		# init plwtemplate object (jinja)
		self.myTemplate = PlwTemplate(template_path, static_path)

		# init PlwData (data content to html/json)
		self.myData = PlwData(self.myTemplate)

		# init PlwScan (index content)
		self.myScan = PlwScan(static_idx_path)

		# dict for index generated from plwidx.scan call,
		# used after in plwdata as { idxname : json full pathname }
		self.myData.idxjson = {}

		# directories for geting data and creating html
		# and be sure static has end \
		if not input_path[-1] == '\\':
			input_path = input_path + '\\'
		self.static = static_path
		self.myData.home_url = home_url
		self.myData.source_path = input_path
		self.original_source_path = input_path
		self.myData.source_data = profile_path
		self.myData.content_path = data_path
		# path in static dir where idx json files are generated
		self.myData.idxjson_path = static_idx_path

		# url defined for jinja templates
		self.myData.root_url = root_url
		self.myData.fw_url = fw_url
		self.myData.static_url = static_url
		self.myData.profile = {}
		self.static_url = static_url

		# webmaster string in jinja head
		self.myData.webmaster = WEBMASTER

		# stop build if errors
		self.stopIfError = False
		self.noError = True

		# log variables
		logger.debug("ZEN PlwInit - Input arguments")
		logger.debug("input_path "+input_path+" (known as source_path)")
		logger.debug("profile_path "+profile_path+" (known as source_data)")
		logger.debug("static_path "+static_path+" (known as static)")
		logger.debug("root_url "+root_url)
		logger.debug("fw_url "+fw_url)
		logger.debug("static_url "+static_url)
		logger.debug("template_path "+template_path)
		logger.debug("data_path "+data_path+ " (known as content_path)")
		logger.debug("static_idx_path "+static_idx_path +" (known as idxjson_path)")
		logger.debug("home_url "+home_url)

	def __del__(self):
		#import pdb; pdb.set_trace()
		dtend = datetime.now()
		d = dtend - self.dtstart
		logger.info("%s end in %s seconds" %("OK" if self.noError == True else "---- ERROR", d))




	# IDX
	def openidx(self, name):
		return self.myScan.openidx(name)
	def closeidx(self):
		return self.myScan.closeidx()

	# ROUTE
	# GENERATE HTML FILE
	def route(self, fdata, ftemplate, fhtml = ''):
		if self.stopIfError is True and self.noError is False:
			logger.critical("Previous error - skip next file : "+fhtml)
			return False
		if not self.myTemplate.is_valid():
			logger.critical("PlwTemplate is not set")
			return False

		logger.info("#")
		# WRITE STATIC WITH DATA AND TEMPLATE
		if not self.myData.load_markdown(fdata):
			logger.critical("EMPTY DATA OR DATA WENT WRONG")
			self.noError = False
			return False
		if ftemplate == '' and fhtml == '':
			self.myData.profile = self.myData.data
			logger.info("LOADING SHARED PROFILE DATA")
			logger.debug(self.myData.profile)
			self.noError = True
		else:
			self.noError = self.myData.write(self.myData.data, ftemplate, fhtml)
		self.myScan.addidx(self.myData.data)
		return self.noError

	# CHANGE DATA PATH
	def sourcepath(self, sou = ''):
		if( sou == '' ):
			sou = self.original_source_path
		self.myData.source_path = sou
		if not self.myData.source_path.endswith('\\'):
			self.myData.source_path = self.myData.source_path + '\\'
		logger.info("#")
		logger.info("# source_path : "+self.myData.source_path)

	# PUSH STATIC
	# 	ADD SUBFOLDER TO STATIC PATH
	#	set variable PWLTEMPLATE static_path
	#	if changecomplete, apply fullpathname, instead relative from PWLINIT
	def pushstatic(self, ffolder = '', fchangecomplete = 0):

		#import pdb; pdb.set_trace()

		if self.stopIfError is True and self.noError is False:
			return False
		if ffolder == '':
			tmppath=self.static
		else:
			if( fchangecomplete == 1 ):
				tmppath = ffolder;
			else:
				if( self.static[-1] != '\\' ):
					tmppath = self.static+"\\"+ffolder
				else:
					tmppath = self.static + ffolder
		#no need ## self.myData.static_url = self.static_url +ffolder+"/"
		self.myTemplate.set_staticpath(tmppath)
		self.myData.static_path = self.myTemplate.static_path

	def getstatic(self):
		return self.myTemplate.static_path

	# PROFILE
	#	SET SHARED COMMUN INFORMATION FROM A SPECIFIC FILE
	def profile(self, fdata):
		if self.stopIfError is True and self.noError is False:
			return False
		logger.info("# load commun profile file : "+fdata)
		self.route(fdata, '', '')

	# ADDIDX
	#	ADDIDX
	def addidx(self, idxname, idxpath):
		self.myData.idxjson[idxname] = idxpath;
		logger.info("add idx [%s] from %s" %(idxname, idxpath))