# import miscellaneous modules
import matplotlib.pyplot as plt
import cv2
import numpy as np
import time

import json
import time
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
import numpy as np
import copy
import itertools
from pycocotools import mask as maskUtils
import os
from collections import defaultdict
import sys
PYTHON_VERSION = sys.version_info[0]
if PYTHON_VERSION == 2:
    from urllib import urlretrieve
elif PYTHON_VERSION == 3:
    from urllib.request import urlretrieve


def _isArrayLike(obj):
	return hasattr(obj, '__iter__') and hasattr(obj, '__len__')


from pycocotools.coco import COCO

class MyCOCO(COCO):
	def showAnns(self, anns, draw_bbox=False):
		"""
		Display the specified annotations.
		:param anns (array of object): annotations to display
		:return: None
		"""
		if len(anns) == 0:
		    return 0
		if 'segmentation' in anns[0] or 'keypoints' in anns[0]:
		    datasetType = 'instances'
		elif 'caption' in anns[0]:
		    datasetType = 'captions'
		else:
		    raise Exception('datasetType not supported')
		if datasetType == 'instances':
		    ax = plt.gca()
		    ax.set_autoscale_on(False)
		    polygons = []
		    color = []
		    for ann in anns:
		        c = (np.random.random((1, 3))*0.6+0.4).tolist()[0]
		        if 'segmentation' in ann:
		            if type(ann['segmentation']) == list:
		                # polygon
		                for seg in ann['segmentation']:
		                    poly = np.array(seg).reshape((int(len(seg)/2), 2))
		                    polygons.append(Polygon(poly))
		                    color.append(c)
		            else:
		                # mask
		                t = self.imgs[ann['image_id']]
		                if type(ann['segmentation']['counts']) == list:
		                    rle = maskUtils.frPyObjects([ann['segmentation']], t['height'], t['width'])
		                else:
		                    rle = [ann['segmentation']]
		                m = maskUtils.decode(rle)
		                img = np.ones( (m.shape[0], m.shape[1], 3) )
		                if ann['iscrowd'] == 1:
		                    color_mask = np.array([2.0,166.0,101.0])/255
		                if ann['iscrowd'] == 0:
		                    color_mask = np.random.random((1, 3)).tolist()[0]
		                for i in range(3):
		                    img[:,:,i] = color_mask[i]
		                ax.imshow(np.dstack( (img, m*0.5) ))
		        if 'keypoints' in ann and type(ann['keypoints']) == list:
		            # turn skeleton into zero-based index
		            sks = np.array(self.loadCats(ann['category_id'])[0]['skeleton'])-1
		            kp = np.array(ann['keypoints'])
		            x = kp[0::3]
		            y = kp[1::3]
		            v = kp[2::3]
		            for sk in sks:
		                if np.all(v[sk]>0):
		                    plt.plot(x[sk],y[sk], linewidth=3, color=c)
		            plt.plot(x[v>0], y[v>0],'o',markersize=8, markerfacecolor=c, markeredgecolor='k',markeredgewidth=2)
		            plt.plot(x[v>1], y[v>1],'o',markersize=8, markerfacecolor=c, markeredgecolor=c, markeredgewidth=2)
		        if draw_bbox:
		            [bbox_x, bbox_y, bbox_w, bbox_h] = ann['bbox']
		            poly = [[bbox_x, bbox_y], [bbox_x, bbox_y+bbox_h], [bbox_x+bbox_w, bbox_y+bbox_h], [bbox_x+bbox_w, bbox_y]]
		            np_poly = np.array(poly).reshape((4,2))
		            polygons.append(Polygon(np_poly))
		            color.append(c)
		            ax.add_patch(Polygon(np_poly, linestyle='--', facecolor='none', edgecolor=c, linewidth=2))

		    p = PatchCollection(polygons, facecolor=color, linewidths=0, alpha=0.4)
		    ax.add_collection(p)
		    p = PatchCollection(polygons, facecolor='none', edgecolors=color, linewidths=2)
		    ax.add_collection(p)
		elif datasetType == 'captions':
			for ann in anns:
				print(ann['caption'])


def viewImages(img_path, segments, all_set, save_path=None, limit=None, original=False, begin_from=0, anns_path=None):

	score = 1
	limit = 100

	import json
	import os

	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
		savedvars = json.load(f)
	path = savedvars['datapath']

	images_path = path + "datasets/coco/images/"
	ann_path = path + "datasets/coco/annotations/"
	ann_orig_path = path + 'datasets/modanet/annotations/'
	snp_path = path + "results/snapshots"

	from keras_maskrcnn.utils.visualization import draw_mask
	from keras_retinanet.utils.visualization import draw_box, draw_caption, draw_annotations
	from keras_retinanet.utils.image import read_image_bgr
	from keras_retinanet.utils.colors import label_color
	from pycocotools import mask as maskUtils
	
	# from . import MyCOCO

	# import miscellaneous modules
	import matplotlib.pyplot as plt
	import cv2
	import numpy as np
	import time

	coco = MyCOCO(ann_path + 'instances_all.json')

	# load annotations
	if original:
		with open(ann_orig_path + 'modanet2018_instances_train.json') as f:
			instances = json.load(f)
		title = ann_orig_path + 'modanet2018_instances_train.json'
	elif anns_path:
		with open(anns_path) as f:
			instances = json.load(f)
		title = anns_path
	else:
		with open(ann_path + 'instances_all.json') as f:
			instances = json.load(f)
		title = ann_path + 'instances_all.json'
	titleshort = title.split("/")[-1]


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
	
	# load label to names mapping for visualization purposes
	labels_to_names = {0: 'bag', 1: 'belt', 2: 'boots', 3: 'footwear', 4: 'outer', 5: 'dress', 6: 'sunglasses', 7: 'pants', 8: 'top', 9: 'shorts', 10: 'skirt', 11: 'headwear', 12: 'scarf/tie'}

	default_save_path = False
	if save_path == 'default':
		# set path to default
		save_path = path + 'results/processedimages/'#images/1.jpg'
		if not annotations:
			save_path += 'images/'
		elif annotations:
			save_path += 'annotations/'
		default_save_path = True
	SAVE_PATH = save_path # used for multiple images


	# now the juicy part: loading the image/s.
	# if img_path, ask again at the end to save time if you want to see multiple files quickly.

	while True:

		if all_set:
			# load images
			
			images = instances['images']

			for ann in instances['annotations']:
				images_anns[ann['image_id']].append(ann)


		elif img_path:
			# just draw the image selected
			img_id = images_ids[img_path]
			for img in instances['images']:
				if img['file_name'] == img_path:
					images = [img]

			for ann in instances['annotations']:
				if ann['image_id'] == img_id:
					images_anns[img_id].append(ann)

		try:
			#for each image in the dataset
			for i, img in enumerate(images[begin_from:]):
				print(i, end=' ')
				if limit and i >= limit:
					break


				image = read_image_bgr(images_path + img['file_name'])

				# if default_save_path:
				# 	if img_path or all_set:
				# 		img_file_name = img['file_name'].split("/")[-1]

				# 		save_path += img_file_name

				# if save_path and segments:
				# 	#remove the extension
				# 	save_path = save_path.split('.')[0]


				# copy to draw on
				draw = image.copy()
				draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

				img_id = img['id']

				plt.figure(num=img['file_name'] + ' – ' + titleshort)

				plt.imshow(draw); plt.axis('off'); plt.tight_layout()
				coco.showAnns(images_anns[img_id])

				plt.show()

				segment_id = 0
				# visualize detections
				for ann in images_anns[img_id]:
					break
					box = ann['bbox']
					label = ann['category_id'] - 1 # they start from 1 in the annotations
					segmentation = ann['segmentation']

					box[2] += box[0]
					box[3] += box[1]

					color = label_color(label)

					#mask = mask_utils.decode(np.asfortranarray(segmentation))

					if not segments:
						b = np.array(box)
						draw_box(draw, b, color=color)
						
						#draw_mask(draw, b, mask, color=label_color(label))

						caption = "{}".format(labels_to_names[label])
						draw_caption(draw, b, caption)
					elif segments:
						drawclone = np.copy(draw)

						b = np.array(box)
						draw_box(drawclone, b, color=color)

						
						#draw_mask_only(drawclone, b, mask, color=label_color(label))

						caption = "{} {:.3f}".format(labels_to_names[label], score)
						draw_caption(drawclone, b, caption)
						plt.figure(figsize=(15, 15))
						plt.axis('off')
						plt.imshow(drawclone)
						if not save_path:
							plt.show()
						elif save_path:
							segment_path = '_segment_' + segment_id + '.jpg'
							save_path_segment = save_path + segment_path
							print(save_path_segment)
							plt.savefig(save_path_segment)
							plt.close()

						
					segment_id += 1
							
				# if not segments:    
				# 	plt.figure(figsize=(15, 15))
				# 	plt.axis('off')
				# 	plt.imshow(draw)
				# 	if not save_path:

				# 		print(img['file_name'])
				# 		plt.show()
				# 	elif save_path:
				# 		print(save_path)
				# 		plt.savefig(save_path)
				# 		plt.close()
				
				save_path = SAVE_PATH # restore path for next image

		except KeyboardInterrupt:
			pass

		if img_path:
			img_path = input('Enter another image to view (press enter to exit):\n')
		else:
			break
		if not img_path:
				break
