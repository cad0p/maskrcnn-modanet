


def viewAnnotations(img_path):

	import json
	import os

	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
		savedvars = json.load(f)
	path = savedvars['datapath']

	images_path = path + "datasets/coco/images/"
	ann_path = path + "datasets/coco/annotations/"
	snp_path = path + "results/snapshots"


	# load annotations
	with open(ann_path + 'instances_all.json') as f:
			instances = json.load(f)


	images_ids = {
		'file_name': 'id'
	}

	#images_filenames = [None] * 1115985


	for img in instances['images']:
		images_ids[img['file_name']] = img['id']
		#images_filenames[img['id']] = img['file_name']


	# images_anns contains all the annotations for each image_id. 
	# the key is the image_id, 
	# the value is a list of the annotations for that id
	images_anns = [ [] for i in range(1115985) ]
	
	img_id = images_ids[img_path]
	for img in instances['images']:
		if img['file_name'] == img_path:
			images = [img]

	for ann in instances['annotations']:
		if ann['image_id'] == img_id:
			images_anns[img_id].append(ann)

	return images_anns[img_id]