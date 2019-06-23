"""CLI validation."""

import os
from click import BadParameter

def check_if_folder_exists(ctx, param, value):
	""" check_if_folder_exists and if not, create it """
	# making path absolute
	value = os.path.abspath(value)
	if not os.path.exists(value):
		os.makedirs(value)
	
	return value + '/'


def check_if_file_exists(ctx, param, value):
	""" check_if_file_exists and if not, raise error """
	# making path absolute
	if value == None: return value
	value = os.path.abspath(value)
	if not os.path.isfile(value):
		raise BadParameter("This file doesn't exist.", ctx, param)
	return value

def check_if_image_exists_in_dataset(ctx, param, value):
	''' check_if_image_exists_in_dataset and if not, raise error '''
	import json
	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
		savedvars = json.load(f)
	path = savedvars['datapath']
	images_path = path + "datasets/coco/images/"
	#making path absolute
	value_path = images_path + value

	# checking if image exists in dataset
	if not os.path.isfile(value_path):
		raise BadParameter("This image doesn't exist in the database. Check if your input is similar to \'01234.jpg\'", ctx, param)
	return value

def check_if_url_downloadable(ctx, param, value):
	''' check_if_url_downloadable and raise error if not '''
	if value == None: return value

	if not is_downloadable(value):
		raise BadParameter("This url can't be downloaded.", ctx, param)
	return value

def is_downloadable(url):
	"""
	Does the url contain a downloadable resource
	"""
	from requests import head
	h = head(url, allow_redirects=True)
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

def check_if_score_is_valid(ctx, param, value):
	''' check_if_score_is_valid and if not raise error (score between 0 and 1) '''
	if not (0 <= value <= 1):
		raise BadParameter("The threshold score must be between 0 and 1.", ctx, param)
	return value