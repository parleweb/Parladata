import sys, os, argparse
import yaml
import logging
from .log import logger

def args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-c', '--commit', help='[nom de commit] sauvegarde le travail en package pour versionning')
	parser.add_argument('-p', '--production', help='[0 = local] [1 = production] génère les fichiers html dans le répertoire local ou production', default=0)
	parser.add_argument('-v', '--verbose', help='[1] log en mode debug', default=0)
	parser.add_argument('-i', '--idx', help='[1] do just indexes', default=0)
	parser.add_argument('-a', '--action', help='define wich action to execute, depends on build script', default=0)
	args = parser.parse_args()
	return args

class PlwConfig():
	def __init__(self, profilename = ''):
		self.profilename = profilename
		self.config = {}
		if( profilename != ''):
			logger.info("--- PARLADATA BUILD WITH "+profilename)
			self.config = self.read(profilename)

	def save(self, fname, dictcfg):
		if( fname.find('.yaml') == -1):
			fname += '.yaml'

		with open(fname, 'w') as hfile:
			yaml.dump(dictcfg, hfile, default_flow_style=False)

	def read(self, fname):
		profile = fname
		if( fname.find('.yaml') == -1):
			fname += '.yaml'
		try:
			with open(fname, 'r') as hfile:
				dictcfg = yaml.load(hfile)
			self.profilename = profile
			self.config = dictcfg
		except FileNotFoundError as e:
			logger.critical("Can't open configuration file "+fname)
			dictcfg = None
		return dictcfg

	def init(self, input_path, profile_path, static_path, root_url, fw_url, static_url, template_path, data_path, static_idx_path, home_url, fdebug = 0, webmaster = 'parladata'):
		dictcfg =  {
		'profile' : self.profilename,
		'build' :
		{
		'source_path' : input_path,
		'profile_path' : profile_path,
		'static_path' : static_path,
		'root_url' : root_url,
		'fw_url' : fw_url,
		'static_url' : static_url,
		'template_path' : template_path,
		'data_path' : data_path,
		'static_idx_path' : static_idx_path,
		'home_url' : home_url,
		'fdebug' : fdebug,
		'webmaster' : webmaster
		}
		}
		self.save(self.profilename, dictcfg)
