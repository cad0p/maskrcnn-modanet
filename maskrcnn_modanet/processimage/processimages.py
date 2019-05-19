import json
import os

with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
	savedvars = json.load(f)
path = savedvars['datapath']

img_path = path + "datasets/coco/images/"
ann_path = path + "datasets/coco/annotations/"
snp_path = path + "results/snapshots"


def get_session():
	import tensorflow as tf

	config = tf.ConfigProto()
	config.gpu_options.allow_growth = True
	return tf.Session(config=config)

def main(proc_img_path=None, all_set=True, save_path=None, model_path=None):
	# import keras
	import keras

	# import keras_retinanet
	from keras_maskrcnn import models
	from keras_maskrcnn.utils.visualization import draw_mask
	from keras_retinanet.utils.visualization import draw_box, draw_caption, draw_annotations
	from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
	from keras_retinanet.utils.colors import label_color

	# import miscellaneous modules
	import matplotlib.pyplot as plt
	import cv2
	import numpy as np
	import time

	# set tf backend to allow memory to grow, instead of claiming everything
	import tensorflow as tf

	# use this environment flag to change which GPU to use
	#os.environ["CUDA_VISIBLE_DEVICES"] = "1"

	# set the modified tf session as backend in keras
	keras.backend.tensorflow_backend.set_session(get_session())

	# adjust this to point to your trained model
	if model_path == None:
		# get all models names in the results folder
		modelnames = [f for f in listdir(snp_path) if isfile(join(snp_path, f))]
		import re

		def extract_number(f):
		    s = re.findall("\d+$",f)
		    return (int(s[0]) if s else -1,f)
		# get the model name with the highest epoch
		print(max(modelnames,key=extract_number))
		model_path = os.path.join(snp_path, max(modelnames,key=extract_number))

	# load retinanet model
	model = models.load_model(model_path, backbone_name='resnet50')
	#print(model.summary())

	# load label to names mapping for visualization purposes
	labels_to_names = {0: 'bag', 1: 'belt', 2: 'boots', 3: 'footwear', 4: 'outer', 5: 'dress', 6: 'sunglasses', 7: 'pants', 8: 'top', 9: 'shorts', 10: 'skirt', 11: 'headwear', 12: 'scarf/tie'}

	if all_set: #STILL TO FIX: ALL_SET OPTION DOESN'T NEED PROC_IMG_PATH
		# load images
		with open(ann_path + 'instances_val.json') as f:
			instances = json.load(f)
		images = instances['images']

	else:
		# just draw the image selected
		images = [read_image_bgr(proc_img_path)]

	#for each image in the dataset
	for img in instances['images']:


		image = read_image_bgr(img_path + img['file_name'])

		# copy to draw on
		draw = image.copy()
		draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

		# preprocess image for network
		image = preprocess_image(image)
		image, scale = resize_image(image)

		# process image
		start = time.time()
		outputs = model.predict_on_batch(np.expand_dims(image, axis=0))
		print("processing time: ", time.time() - start)

		boxes  = outputs[-4][0]
		scores = outputs[-3][0]
		labels = outputs[-2][0]
		masks  = outputs[-1][0]

		# correct for image scale
		boxes /= scale

		# visualize detections
		for box, score, label, mask in zip(boxes, scores, labels, masks):
		    if score < 0.5:
		        break

		    color = label_color(label)
		    
		    b = box.astype(int)
		    draw_box(draw, b, color=color)
		    
		    mask = mask[:, :, label]
		    draw_mask(draw, b, mask, color=label_color(label))
		    
		    caption = "{} {:.3f}".format(labels_to_names[label], score)
		    draw_caption(draw, b, caption)
		    
		plt.figure(figsize=(15, 15))
		plt.axis('off')
		plt.imshow(draw)
		plt.show()