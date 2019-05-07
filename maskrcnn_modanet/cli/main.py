import click, json

from . import validators


@click.group()
def main():
	"""Main CLI."""
	pass


@main.group()
def datasets():
	''' Manage your datasets '''


@datasets.command()
@click.argument('path', callback=validators.check_if_folder_exists)
def download(path):
	''' Choose datasets folder. 
		It will be about 50 GB 

	(of which most can be deleted afterwards if not wanted)
	 '''
	import os, subprocess


	#running bash commands
	print(path)
	dir_cli_path = os.path.dirname(os.path.realpath(__file__))
	dir_pkg_path = "/".join(dir_cli_path.split("/")[:-1]) + "/"
	print(dir_pkg_path)

	print('''downloading paperdoll dataset
			taken from here:
			https://github.com/kyamagu/paperdoll/tree/master/data/chictopia
			''')

	os.system("sh " + dir_pkg_path + "download.sh '" + path + "'")
	

	savedvars = {
		'datapath': path
	}

	with open(dir_pkg_path + 'savedvars.json', 'w') as outfile:
		json.dump(savedvars, outfile)


@datasets.command()
def prepare():
	''' Prepares the dataset for training!

	'''