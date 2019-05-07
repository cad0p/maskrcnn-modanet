"""CLI validation."""

import os


def check_if_folder_exists(ctx, param, value):
	""" check_if_folder_exists and if not, create it """
	if not os.path.exists(value):
		os.makedirs(value)
	
	return value + '/'