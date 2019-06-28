

def evaluateModel(model_path):

	import json
	import os

	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
		savedvars = json.load(f)
	path = savedvars['datapath']

	ann_path = path + "datasets/coco/annotations/"
	ann_orig_path = path + 'datasets/modanet/annotations/'

	coco_path = path + "datasets/coco/"

	from keras_maskrcnn import models

	model = models.load_model(model_path, backbone_name='resnet50')

	from keras_retinanet.utils.transform import random_transform_generator

	transform_generator = random_transform_generator(flip_x_chance=0.5)

	from maskrcnn_modanet.train.coco import CocoGenerator

	validation_generator = CocoGenerator(
            coco_path,
            'val',
            batch_size=1,
            config=None,
            image_min_side=800,
            image_max_side=1333
        )

	from keras_maskrcnn.utils.coco_eval import evaluate_coco

	evaluate_coco(validation_generator, model)