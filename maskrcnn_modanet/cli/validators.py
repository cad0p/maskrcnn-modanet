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