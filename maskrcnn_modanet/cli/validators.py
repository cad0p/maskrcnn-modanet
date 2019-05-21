"""CLI validation."""

import os


def check_if_folder_exists(ctx, param, value):
	""" check_if_folder_exists and if not, create it """
	# making path absolute
	value = os.path.abspath(value)
	if not os.path.exists(value):
		os.makedirs(value)
	
	return value + '/'


def check_if_file_exists(ctx, param, value):
	""" check_if_file_exists and if not, ask again """
	# making path absolute
	if value == None: return value
	value = os.path.abspath(value)
	while not os.path.isfile(value):
		value = os.path.abspath(input("This file doesn't exist. Insert it again here: "))
	return value

def check_if_url_downloadable(ctx, param, value):
	''' check_if_url_downloadable '''
	if value == None: return value

	while not is_downloadable(value):
		value = input("This url can't be downloaded. Insert it again here: ")
	return value

def is_downloadable(url):
	"""
	Does the url contain a downloadable resource
	"""
	import requests
	h = requests.head(url, allow_redirects=True)
	header = h.headers
	content_type = header.get('content-type')
	if 'text' in content_type.lower():
	    return False
	if 'html' in content_type.lower():
	    return False
	return True

def check_if_file_folder_exists(ctx, param, value):
	""" check_if_file_folder_exists and if not, create it """
	if value == None or value == 'default':
		return value
	# making path absolute
	value = os.path.abspath(value)
	value_folder = os.path.dirname(value)
	if not os.path.exists(value_folder):
		os.makedirs(value_folder)
	
	return value