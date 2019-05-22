import click, json, os

from . import validators
from maskrcnn_modanet.processimage import processimages


def print_help(ctx, param, value):
    if value is False:
        return
    click.echo(ctx.get_help())
    ctx.exit()

@click.group()
def main():
	"""Main CLI."""
	pass


@main.group()
def datasets():
	''' Manage your datasets


	run 
	  \n\n1 -> maskrcnn-modanet datasets download [your path here]
	  	\n2 -> maskrcnn-modanet datasets arrange
	 '''
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

@main.group()
def processimage():
	''' View and save processed image and annotations from input image '''
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
	exceptions = ['pkgpath', 'savedvarspath']

	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
		savedvars = json.load(f)
	if variable not in exceptions:
		savedvars[variable] = newvalue
	else:
		print("The variable " + variable + " is view only. Value not modified")

	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json', 'w') as outfile:
		json.dump(savedvars, outfile)



@processimage.group()
def view():
	''' View result. image or annotations '''
	pass

@processimage.group()
def save():
	''' Save result. image or annotations '''
	pass

@view.command()
@click.option('-p', '--proc-img-path', callback=validators.check_if_file_exists)
@click.option('-u', '--proc-img-url', callback=validators.check_if_url_downloadable)
@click.option('-s', '--segments', is_flag=True, default=False, help='For every annotation found in the image')
@click.option('-a', '--all-set', is_flag=True, default=False, help='Results for each image in the validation set')
@click.option('-m', '--model-path', default=None, callback=validators.check_if_file_exists, help='If you want to use a custom model other than the best one found in results')
@click.pass_context
def image(ctx, proc_img_path, proc_img_url, segments, all_set, model_path):
	''' Show processed image '''
	
	if (not segments or (segments and not all_set) ) and ((1 if proc_img_path else 0)+(1 if proc_img_url else 0)+(1 if all_set else 0)) == 1:
		processimages.main(proc_img_path, proc_img_url, all_set, None, model_path, segments, False)
	else:
		print_help(ctx, None,  value=True)

@view.command()
@click.option('-p', '--proc-img-path', callback=validators.check_if_file_exists)
@click.option('-u', '--proc-img-url', callback=validators.check_if_url_downloadable)
@click.option('-m', '--model-path', default=None, callback=validators.check_if_file_exists, help='If you want to use a custom model other than the best one found in results')
@click.pass_context
def annotations(ctx, proc_img_path, proc_img_url, model_path):
	''' Show processed image annotations '''
	segments = True; all_set = False
	if (not segments or (segments and not all_set) ) and ((1 if proc_img_path else 0)+(1 if proc_img_url else 0)+(1 if all_set else 0)) == 1:
		print(processimages.main(proc_img_path, proc_img_url, False, None, model_path, segments, True)) #function returns the annotations
	else:
		print_help(ctx, None,  value=True)


@save.command()
@click.option('-p', '--proc-img-path', callback=validators.check_if_file_exists)
@click.option('-u', '--proc-img-url', callback=validators.check_if_url_downloadable)
@click.option('-s', '--segments', is_flag=True, default=False, help='For every annotation found in the image')
@click.option('-a', '--all-set', is_flag=True, default=False, help='Results for each image in the validation set')
@click.option('-m', '--model-path', default=None, callback=validators.check_if_file_exists, help='If you want to use a custom model other than the best one found in results')
@click.option('--save-path', default='default', callback=validators.check_if_file_folder_exists, help='Set your save path (including extension .jpg). Defaults inside the processimages folder')
@click.pass_context
def image(ctx, proc_img_path, proc_img_url, save_path, segments, all_set, model_path):
	''' Save processed image '''
	if (not segments or (segments and not all_set) ) and ((1 if proc_img_path else 0)+(1 if proc_img_url else 0)+(1 if all_set else 0)) == 1:
		processimages.main(proc_img_path, proc_img_url, False, None, model_path, False, False)
	else:
		print_help(ctx, None,  value=True)

@save.command()
@click.option('-p', '--proc-img-path', callback=validators.check_if_file_exists)
@click.option('-u', '--proc-img-url', callback=validators.check_if_url_downloadable)
@click.option('-m', '--model-path', default=None, callback=validators.check_if_file_exists, help='If you want to use a custom model other than the best one found in results')
@click.option('--save-path', default='default', callback=validators.check_if_file_folder_exists, help='Set your save path (including extension .jpg). Defaults inside the processimages folder')
@click.pass_context
def annotations(ctx, proc_img_path, proc_img_url, save_path, model_path):
	''' Save processed image annotations '''
	segments = True; all_set = False
	if (not segments or (segments and not all_set) ) and ((1 if proc_img_path else 0)+(1 if proc_img_url else 0)+(1 if all_set else 0)) == 1:
		processimages.main(proc_img_path, proc_img_url, False, save_path, model_path, segments, True)
	else:
		print_help(ctx, None,  value=True)
