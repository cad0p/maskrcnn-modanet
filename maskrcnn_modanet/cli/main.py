import click, json, os

from maskrcnn_modanet.cli import validators

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

@main.command()
@click.option('-p', '--img-path', callback=validators.check_if_image_exists_in_dataset, help='Only the image filename, like \'01234.jpg\'. It must be in the dataset\'s images folder')
@click.option('-m', '--anns-path', default=None, callback=validators.check_if_file_exists, help='The path to the custom annotations file you want to use (m letter is used for similarity to the --model-path)')
@click.option('-s', '--segments', is_flag=True, default=False, help='For every annotation found in the image')
@click.option('-a', '--all-set', is_flag=True, default=False, help='Results for each image in all the dataset')
@click.option('-b', '--begin-from', default=0, help='If \'all-set\', you can select from which image in the annotations\' index to begin by putting the number here')
@click.option('-o', '--original', is_flag=True, default=False, help='Use the original annotations, not fixed.')
@click.option('-c', '--coco-way', is_flag=True, default=False, help='Use the coco api to see the masks annotations. Do not use if you want to see bboxes')
@click.pass_context
def viewimage(ctx, img_path, segments, all_set, coco_way, original,begin_from, anns_path):
	''' View and (not yet needed) save dataset images, plain (not yet needed) or annotated. Useful to check the dataset annotations on the dataset and compare them with the prediction!
		Runs without GPU need '''
	if not coco_way:
		from maskrcnn_modanet.viewimages import viewImages
	else:
		from maskrcnn_modanet.viewimagescoco import viewImages

	if (not segments or (segments and not all_set) ) and ((1 if img_path else 0)+(1 if all_set else 0)) == 1:
		viewImages(img_path, segments, all_set, original=original,begin_from=begin_from,anns_path=anns_path)
	else:
		print_help(ctx, None,  value=True)


@main.command()
@click.option('-p', '--img-path', callback=validators.check_if_image_exists_in_dataset, help='Only the image filename, like \'01234.jpg\'. It must be in the dataset\'s images folder')
@click.option('-m', '--anns-path', default=None, callback=validators.check_if_file_exists, help='The path to the custom annotations file you want to use (m letter is used for similarity to the --model-path)')
@click.option('-o', '--original', is_flag=True, default=False, help='Use the original annotations, not fixed.')
@click.pass_context
def viewannotation(ctx, img_path, original, anns_path):
	''' View and (not yet needed) save dataset images, plain (not yet needed) or annotated. Useful to check the dataset annotations on the dataset and compare them with the prediction!
		Runs without GPU need '''
	from maskrcnn_modanet.viewannotations import viewAnnotations
	if img_path:
		print(viewAnnotations(img_path, original, anns_path=anns_path))
	else:
		print_help(ctx, None,  value=True)

@main.command()
@click.option('-m', '--model-path', default=None, callback=validators.check_if_file_exists, help='The path to the .h5 model you want to evaluate (usually in results/snapshots)')
@click.pass_context
def evaluate(ctx, model_path):
	''' Evaluate any trained model, average precision and recall. '''
	from maskrcnn_modanet.evaluatemodel import evaluateModel
	if model_path:
		evaluateModel(model_path)
	else:
		print_help(ctx, None,  value=True)


@main.command()
@click.option('-p', '--profile', default=None, help='The instagram profile username you want the statistics on.')
@click.option('-r', '--restore-result', is_flag=True, default=False, help='Restore the last result in order not to process thousands of images multiple times when not needed.')
@click.option('-l', '--limit', default=None, type=int, help='If an instagram profile is big and you want to use the most recent images only.')
@click.option('-o', '--offset', default=0, type=int, callback=validators.validate_offset, 
	help='If you want to view the images from a certain post. Counted from most recent. To use with limit option.')
@click.option('-c', '--choice', default=None, help='Choose between \'i\' and \'s\'. i if you want to see the resulting images visually, s if you want to see the statistics. It will be asked to you during the program, otherwise.')
@click.pass_context
def instagram(ctx, profile, limit, offset, choice, restore_result):
	''' Simple implementation to track instagram metrics per profile. '''
	from maskrcnn_modanet.instagram_impl import instagramImpl
	if profile:
		instagramImpl(profile, limit=limit, offset=offset, choice=choice, restore_result=restore_result)
	else:
		print_help(ctx, None,  value=True)

@datasets.command()
@click.argument('path', callback=validators.check_if_folder_exists)
def download(path):
	''' Choose datasets folder. 
		It will be about 50 GB 

	(of which most can be deleted afterwards if not wanted)

	if you already have the photos.lmdb file lying around, just wait until the program starts
	downloading it, stop it and put the file into the ./datasets/paperdoll/data/chictopia folder.
	 '''


	#running bash commands
	print(path)
	dir_cli_path = os.path.dirname(os.path.realpath(__file__))
	dir_pkg_path = "/".join(dir_cli_path.split("/")[:-1]) + "/"
	print(dir_pkg_path)

	slow_download = input('Do you want to download the whole 1 million images (what I had to do) or to just download the 50k annotated with ModaNet?\nY for 1 million (40 GB), N for 50k: ')

	if slow_download in ['y', 'Y']:
		slow_download = True
	else:
		slow_download = False

	fast_download = not slow_download

	print('''downloading paperdoll dataset
			taken from here:
			https://github.com/kyamagu/paperdoll/tree/master/data/chictopia
			''')

	failure = os.system("sh " + dir_pkg_path + "download.sh '" + path + "' " + str(fast_download) )

	if failure:
		print('Bash script failed. Run again this command after having downloaded the necessary packages')
		exit()

	
	print("If you don't have tree installed, just install it for bash terminal and run this command again: \nmaskrcnn-modanet datasets download")	
	print("\nThis command also stores your saved variables with the default values. run 'maskrcnn-modanet savedvars show' to see them")
	savedvars = {
		'savedvarspath': os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json',
		'fast_download': str(fast_download),
		'datapath': path,
		'pkgpath': dir_pkg_path,
		'seed' : None,
		'percentagetrain' : None,
		'percentageval' : None,
		'percentagetest' : None
	}

	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json', 'w') as outfile:
		json.dump(savedvars, outfile)

	print('\n\nNow run \'maskrcnn-modanet datasets arrange\'\n\n')


@datasets.command()
def arrange():
	''' Arranges the dataset for training!

	'''
	from .. import arrange_images
	from .. import arrange_annotations

@datasets.command()
def fix():
	''' Fixes the annotations' errors.
	
		ModaNet annotations have some bounding boxes not aligned with the mask,
		particularly so with footwear and boots, where both feet have the same
		bounding box x1 and y1 (position of upper-left corner of box),
		but the correct shape (x2, y2 are the width and height)

		You can always revert back by deleting instances_all.json and arranging
		the dataset again.
	'''
	from maskrcnn_modanet import fix_annotations

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
@click.option('-p', '--proc-img-path')
@click.option('-u', '--proc-img-url', callback=validators.check_if_url_downloadable)
@click.option('-s', '--segments', is_flag=True, default=False, help='For every annotation found in the image')
@click.option('-a', '--all-set', is_flag=True, default=False, help='Results for each image in the validation set')
@click.option('-mt', '--model-type', default='default', callback=validators.check_if_model_type_valid, help='Set \'trained\' for your last trained snapshot on the snapshots folder, \'coco\' for the image recognition of the COCO dataset. \'default\' is the default value and is the pretrained modanet snapshot you downloaded in the results folder.')
@click.option('-m', '--model-path', default=None, callback=validators.check_if_file_exists, help='If you want to use a custom model other than the best one found in results')
@click.option('-t', '--threshold-score', default=0.5, callback=validators.check_if_score_is_valid, help='Set the lowest level of confidence to show annotations for the image')
@click.pass_context
def image(ctx, proc_img_path, proc_img_url, segments, all_set, model_path, threshold_score, model_type):
	''' Show processed image '''
	from maskrcnn_modanet import processimages
	
	if (not segments or (segments and not all_set) ) and ((1 if proc_img_path else 0)+(1 if proc_img_url else 0)+(1 if all_set else 0)) == 1:
		model, labels_to_names = processimages.loadModel(model_type=model_type, model_path=model_path)
		processimages.main(proc_img_path, proc_img_url, all_set, None, model_path, segments, False, threshold_score, model=model, labels_to_names=labels_to_names)
	else:
		print_help(ctx, None,  value=True)

@view.command()
@click.option('-p', '--proc-img-path')
@click.option('-u', '--proc-img-url', callback=validators.check_if_url_downloadable)
@click.option('-mt', '--model-type', default='default', callback=validators.check_if_model_type_valid, help='Set \'trained\' for your last trained snapshot on the snapshots folder, \'coco\' for the image recognition of the COCO dataset. \'default\' is the default value and is the pretrained modanet snapshot you downloaded in the results folder.')
@click.option('-m', '--model-path', default=None, callback=validators.check_if_file_exists, help='If you want to use a custom model other than the best one found in results')
@click.option('-t', '--threshold-score', default=0.5, callback=validators.check_if_score_is_valid, help='Set the lowest level of confidence to show annotations for the image')
@click.pass_context
def annotations(ctx, proc_img_path, proc_img_url, model_path, threshold_score, model_type):
	''' Show processed image annotations '''
	from maskrcnn_modanet import processimages
	segments = True; all_set = False
	if (not segments or (segments and not all_set) ) and ((1 if proc_img_path else 0)+(1 if proc_img_url else 0)+(1 if all_set else 0)) == 1:
		model, labels_to_names = processimages.loadModel(model_type=model_type, model_path=model_path)
		print(processimages.main(proc_img_path, proc_img_url, False, None, model_path, segments, True, threshold_score, model=model, labels_to_names=labels_to_names)) #function returns the annotations
	else:
		print_help(ctx, None,  value=True)


@save.command()
@click.option('-p', '--proc-img-path')
@click.option('-u', '--proc-img-url', callback=validators.check_if_url_downloadable)
@click.option('-s', '--segments', is_flag=True, default=False, help='For every annotation found in the image')
@click.option('-a', '--all-set', is_flag=True, default=False, help='Results for each image in the validation set')
@click.option('-l', '--limit', default=None, type=int, help='Works with option -a. Only saves the first l number of results')
@click.option('-mt', '--model-type', default='default', callback=validators.check_if_model_type_valid, help='Set \'trained\' for your last trained snapshot on the snapshots folder, \'coco\' for the image recognition of the COCO dataset. \'default\' is the default value and is the pretrained modanet snapshot you downloaded in the results folder.')
@click.option('-m', '--model-path', default=None, callback=validators.check_if_file_exists, help='If you want to use a custom model other than the best one found in results')
@click.option('-t', '--threshold-score', default=0.5, callback=validators.check_if_score_is_valid, help='Set the lowest level of confidence to show annotations for the image')
@click.option('--save-path', default='default', callback=validators.check_if_file_folder_exists, help='Set your save path (including extension .jpg). Defaults inside the processimages folder')
@click.pass_context
def image(ctx, proc_img_path, proc_img_url, save_path, segments, all_set, model_path, threshold_score, limit, model_type):
	''' Save processed image '''
	from maskrcnn_modanet import processimages

	if (not segments or (segments and not all_set) ) and ((1 if proc_img_path else 0)+(1 if proc_img_url else 0)+(1 if all_set else 0)) == 1:
		model, labels_to_names = processimages.loadModel(model_type=model_type, model_path=model_path)
		processimages.main(proc_img_path, proc_img_url, all_set, save_path, model_path, segments, False, threshold_score, limit, model=model, labels_to_names=labels_to_names)
	else:
		print_help(ctx, None,  value=True)

@save.command()
@click.option('-p', '--proc-img-path')
@click.option('-u', '--proc-img-url', callback=validators.check_if_url_downloadable)
@click.option('-mt', '--model-type', default='default', callback=validators.check_if_model_type_valid, help='Set \'trained\' for your last trained snapshot on the snapshots folder, \'coco\' for the image recognition of the COCO dataset. \'default\' is the default value and is the pretrained modanet snapshot you downloaded in the results folder.')
@click.option('-m', '--model-path', default=None, callback=validators.check_if_file_exists, help='If you want to use a custom model other than the best one found in results')
@click.option('-t', '--threshold-score', default=0.5, callback=validators.check_if_score_is_valid, help='Set the lowest level of confidence to show annotations for the image')
@click.option('--save-path', default='default', callback=validators.check_if_file_folder_exists, help='Set your save path (including extension .jpg). Defaults inside the processimages folder')
@click.pass_context
def annotations(ctx, proc_img_path, proc_img_url, save_path, model_path, threshold_score, model_type):
	''' Save processed image annotations '''
	from maskrcnn_modanet import processimages

	segments = True; all_set = False
	if (not segments or (segments and not all_set) ) and ((1 if proc_img_path else 0)+(1 if proc_img_url else 0)+(1 if all_set else 0)) == 1:
		model, labels_to_names = processimages.loadModel(model_type=model_type, model_path=model_path)
		processimages.main(proc_img_path, proc_img_url, False, save_path, model_path, segments, True, threshold_score, model=model, labels_to_names=labels_to_names)
	else:
		print_help(ctx, None,  value=True)
