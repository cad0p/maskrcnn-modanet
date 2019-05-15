import click, json, os

from . import validators


@click.group()
def main():
	"""Main CLI."""
	pass


@main.group()
def datasets():
	''' Manage your datasets '''
	pass


@main.command(name='train', context_settings=dict(
    ignore_unknown_options=True,
))
@click.argument('args', required=False, nargs=-1)
def train(args):
	''' Train using the dataset downloaded
		usage: 
		\n\nmaskrcnn-modanet train [your command to launch a python 3 script] [arguments for the script]
		\n\nthe command to launch a python 3 script could either be python or python3, depending on your machine
		\n\nAn example could be:
		\n\nmaskrcnn-modanet train --epochs 15 --workers 0 --batch-size 0 coco
	'''

	if args == ():
		args = None

	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
		savedvars = json.load(f)
	# os.system(str(pythoncommand) + ' ' + savedvars['pkgpath'] + "train/train.py " + args)
	from maskrcnn_modanet.train.train import main
	main(args)

@main.group()
def savedvars():
	''' Show and edit saved variables '''
	pass

@datasets.command()
@click.argument('path', callback=validators.check_if_folder_exists)
def download(path):
	''' Choose datasets folder. 
		It will be about 50 GB 

	(of which most can be deleted afterwards if not wanted)
	 '''


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
	
	print("If you don't have tree installed, just install it for bash terminal and run this command again: \nmaskrcnn-modanet datasets download")	
	print("\nThis command also stores your saved variables with the default values. run 'maskrcnn-modanet savedvars show' to see them")
	savedvars = {
		'savedvarspath': os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json',
		'datapath': path,
		'pkgpath': dir_pkg_path,
		'seed' : None,
		'percentagetrain' : None,
		'percentageval' : None,
		'percentagetest' : None
	}

	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json', 'w') as outfile:
		json.dump(savedvars, outfile)


@datasets.command()
def arrange():
	''' Arranges the dataset for training!

	'''
	from .. import arrange_images
	from .. import arrange_annotations

@savedvars.command()
def show():
	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
		parsed = json.load(f)
		print(json.dumps(parsed, indent=4, sort_keys=True))

@savedvars.command()
@click.argument('variable')
@click.argument('newvalue', default=None, required=False)
def edit(variable, newvalue):
	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
		savedvars = json.load(f)
	savedvars[variable] = newvalue
	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json', 'w') as outfile:
		json.dump(savedvars, outfile)