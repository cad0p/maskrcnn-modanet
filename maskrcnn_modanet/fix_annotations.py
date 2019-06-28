
def ShapeNearestToFirstMask(shape, mask1, mask2):
	from statistics import mean
	distancemask1 = []
	distancemask2 = []

	shape_bbox = [400, 600, 0, 0]
	for xy_index, xy in enumerate(shape):	
		if xy < shape_bbox[xy_index % 2]:
			shape_bbox[xy_index % 2] = xy
		elif xy - shape_bbox[xy_index % 2] > shape_bbox[xy_index % 2 + 2]:
			shape_bbox[xy_index % 2 + 2] = xy - shape_bbox[xy_index % 2]

	for shape1 in mask1:
		shape_bbox1 = [400, 600, 0, 0]
		for xy_index1, xy1 in enumerate(shape1):	
			if xy1 < shape_bbox1[xy_index1 % 2]:
				shape_bbox1[xy_index1 % 2] = xy1
			elif xy1 - shape_bbox1[xy_index1 % 2] > shape_bbox1[xy_index1 % 2 + 2]:
				shape_bbox1[xy_index1 % 2 + 2] = xy1 - shape_bbox1[xy_index1 % 2]
		distancemask1.append(min(shape_bbox[0] - (shape_bbox1[0] + shape_bbox1[2]),
								shape_bbox[1] - (shape_bbox1[1] + shape_bbox1[3]),
								shape_bbox[0] + shape_bbox[2] - shape_bbox1[0],
								shape_bbox[1] + shape_bbox1[3] - shape_bbox1[1]
								))

	for shape2 in mask2:
		shape_bbox2 = [400, 600, 0, 0]
		for xy_index2, xy2 in enumerate(shape2):	
			if xy2 < shape_bbox2[xy_index2 % 2]:
				shape_bbox2[xy_index2 % 2] = xy2
			elif xy2 - shape_bbox2[xy_index2 % 2] > shape_bbox2[xy_index2 % 2 + 2]:
				shape_bbox2[xy_index2 % 2 + 2] = xy2 - shape_bbox2[xy_index2 % 2]
		distancemask2.append(min(shape_bbox[0] - (shape_bbox2[0] + shape_bbox2[2]),
								shape_bbox[1] - (shape_bbox2[1] + shape_bbox2[3]),
								shape_bbox[0] + shape_bbox[2] - shape_bbox2[0],
								shape_bbox[1] + shape_bbox1[3] - shape_bbox2[1]
								))
	return mean(distancemask1) <= mean(distancemask2)

def maskBbox(shapes):
	shape_bbox = [400, 600, 0, 0]
	for shape in shapes:
		shape_bbox_i = shapeBbox(shape)
		if shape_bbox_i[0] < shape_bbox[0]:
			shape_bbox[0] = shape_bbox_i[0]
		if shape_bbox_i[1] < shape_bbox[1]:
			shape_bbox[1] = shape_bbox_i[1]
		if shape_bbox_i[2] > shape_bbox[2]:
			shape_bbox[2] = shape_bbox_i[2]
		if shape_bbox_i[3] > shape_bbox[3]:
			shape_bbox[3] = shape_bbox_i[3]
	if shape_bbox == [400, 600, 0, 0]:
		import ipdb; ipdb.set_trace()
	return shape_bbox


def shapeBbox(shape):
	shape_bbox = [400, 600, 0, 0]
	for xy_index, xy in enumerate(shape):	
		if xy < shape_bbox[xy_index % 2]:
			shape_bbox[xy_index % 2] = xy
		elif xy - shape_bbox[xy_index % 2] > shape_bbox[xy_index % 2 + 2]:
			shape_bbox[xy_index % 2 + 2] = xy - shape_bbox[xy_index % 2]
	return shape_bbox


def bboxShapeMargin(bbox, shape):
	shape_bbox = [400, 600, 0, 0]
	for xy_index, xy in enumerate(shape):	
		if xy < shape_bbox[xy_index % 2]:
			shape_bbox[xy_index % 2] = xy
		elif xy - shape_bbox[xy_index % 2] > shape_bbox[xy_index % 2 + 2]:
			shape_bbox[xy_index % 2 + 2] = xy - shape_bbox[xy_index % 2]
	return (shape_bbox[0] - bbox[0] + 
			shape_bbox[1] - bbox[1] + 
			bbox[2] - shape_bbox[2] +
			bbox[3] - shape_bbox[3]
			)

def bboxContainsShapes(bbox, shapes, error=0.05):
	shapes_contained = 0
	shapes_total = 0
	for shape in shapes:
		shape_bbox = shapeBbox(shape)
		if bboxContainsShape(bbox, shape):
			shapes_contained += shape_bbox[2] * shape_bbox[3]
		shapes_total += shape_bbox[2] * shape_bbox[3]

	return shapes_contained/shapes_total

def bboxContainsShape(bbox, shape, error=0.05):
	shape_bbox = [400, 600, 0, 0]
	for xy_index, xy in enumerate(shape):	
		if xy < shape_bbox[xy_index % 2]:
			shape_bbox[xy_index % 2] = xy
		elif xy - shape_bbox[xy_index % 2] > shape_bbox[xy_index % 2 + 2]:
			shape_bbox[xy_index % 2 + 2] = xy - shape_bbox[xy_index % 2]

	return (bbox[0] - error * shape_bbox[2] <= shape_bbox[0] and
			bbox[1] - error * shape_bbox[3] <= shape_bbox[1] and
			bbox[2] + error * shape_bbox[2] >= shape_bbox[2] and
			bbox[3] + error * shape_bbox[3] >= shape_bbox[3]
			)

import json
import os

with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
	savedvars = json.load(f)
path = savedvars['datapath']

import copy

import random

import time

timestr = time.strftime("%Y%m%d-%H%M%S")

logs = {}
# log will be saved as file.

ann_path = path + "datasets/coco/annotations/"

if not os.path.isfile(ann_path + 'instances_all.json'):
	# error: the file is needed for fixing the annotatios
	print('ERROR: run \'maskrcnn-modanet datasets arrange\'')
	exit()



print('Now fixing annotations. Just delete the file \'instances_all.json\' and rerun this command, if you want to restore it to the original one.')
print('It is also useful to delete the file above if you run into any issues at all. It will be recreated automatically')


with open(ann_path + 'instances_all.json') as f:
   	instances = json.load(f)

print("Annotations:" + str(len(instances['annotations'])))

images_index = [ None ] * 1115985

# images_anns_indexes contains all the annotations for each image_id. 
# the key is the image_id, 
# the value is a list of the indexes of the annotations for that id in instances['annotations']
images_anns_indexes = [ [] for i in range(1115985) ]

img_ids = []
img_ids_from_anns = []


print('Analyzing the annotations of each image..')

for img_index, img in enumerate(instances['images']):
	img_id = img['id']
	img_ids.append(img_id)
	images_index[img_id] = img_index

for ann_index, ann in enumerate(instances['annotations']):
		img_id = ann['image_id']
		if len(images_anns_indexes[img_id]) == 0:
			img_ids_from_anns.append(img_id)
		images_anns_indexes[img_id].append(ann_index)

print('Finding the wrong ones')
# let's assume the width and height of the bboxes are correct at least.

print('Len img ids:' + str([len(img_ids), len(img_ids_from_anns)]))

if len(img_ids) > len(img_ids_from_anns):
	logs['images_deleted'] = {
		'quantity': None,
		'images': []
	}
	print('Annotations do not cover all the images.')
	print('Deleting the unnecessary images ')
	logs['images_deleted']['quantity'] = len(img_ids) - len(img_ids_from_anns)
	print(str(logs['images_deleted']['quantity']) + ' unnecessary images')
	img_diff = list(set(img_ids) - set(img_ids_from_anns))
	for img_id in img_diff:
		logs['images_deleted']['images'].append(instances['images'][images_index[img_id]])
		del instances['images'][images_index[img_id]]

		# recalculate the index
		images_index = [ None ] * 1115985
		for img_index, img in enumerate(instances['images']):
			img_id = img['id']
			images_index[img_id] = img_index

	print(str(len(instances['images']) - len(img_ids_from_anns)) + ' images difference now.')
	img_ids = img_ids_from_anns

elif len(img_ids) < len(img_ids_from_anns):
	print('ERROR: There are annotations not related to any image.')
	exit()

print('Now looking for bounding boxes that share the same location')

logs['double_anns'] = []
logs['move_box'] = []

counter = 0; counter1 = 0; counter2 = 0; counter3 = 0; counter4 = 0

# i want to find the bboxes that have same starting point and same label
for img_id in img_ids:
	for ann_index1 in images_anns_indexes[img_id]:
		ann1 = instances['annotations'][ann_index1]
		bbox1 = ann1['bbox']
		label1 = ann1['category_id']

		for ann_index2 in images_anns_indexes[img_id]:
			ann2 = instances['annotations'][ann_index2]
			bbox2 = ann2['bbox']
			label2 = ann2['category_id']

			if bbox1[0] == bbox2[0] and bbox1[1] == bbox2[1] and label1 == label2 and ann1['id'] != ann2['id']:
				# try to fit into mask. is one correct, at least?
				mask1 = ann1['segmentation']
				mask2 = ann2['segmentation']

				counter += 1

				wrongbbox1 = False
				wrongbbox2 = False

				for shape_index1, shape1 in enumerate(mask1):
					for shape_index2, shape2 in enumerate(mask2):
						if shape1 == shape2 and shape_index1 != shape_index2:
							if (bboxContainsShape(bbox1, shape1) and not bboxContainsShape(bbox2, shape2) or
									len(instances['annotations'][ann_index1]['segmentation']) == shape_index1
								):
								logs['double_anns'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'shape': shape1,
										'wrong': 2
									})
								wrongbbox2 = True
								del instances['annotations'][ann_index2]['segmentation'][shape_index2]
								# indices problem? seems not. update: it probably works because it directly uses the index
								# update 2 it's a disaster as we could have easily guessed
							elif not bboxContainsShape(bbox1, shape1) and bboxContainsShape(bbox2, shape2):
								logs['double_anns'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'shape': shape1,
										'wrong': 1
									})
								wrongbbox1 = True
								del instances['annotations'][ann_index1]['segmentation'][shape_index1]
							elif not bboxContainsShape(bbox1, shape1) and not bboxContainsShape(bbox2, shape2):
								wrongbbox1 = True
								wrongbbox2 = True
								# weird situation in which all the bboxes are wrong. we need to decide
								# who will go in which mask though, and then fit both the boxes
								# we'll decide based on vicinity score between the masks!
								if (ShapeNearestToFirstMask(shape1, mask1, mask2) or
									len(instances['annotations'][ann_index1]['segmentation']) == shape_index1
									):
									logs['double_anns'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'shape': shape1,
										'wrong': 2
									})
									del instances['annotations'][ann_index2]['segmentation'][shape_index2]
								else:
									logs['double_anns'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'shape': shape1,
										'wrong': 1
									})
									del instances['annotations'][ann_index1]['segmentation'][shape_index1]
							else:
								# they are all correct, but usually in this case the smaller box is the better, so we'll
								# go for it and see the results
								#  to do this we'll 

								if bboxShapeMargin(bbox1, shape1) >= bboxShapeMargin(bbox2, shape2):
									logs['double_anns'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'shape': shape1,
										'wrong': 0
									})
									del instances['annotations'][ann_index1]['segmentation'][shape_index1]
								else:
									logs['double_anns'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'shape': shape2,
										'wrong': 0
									})
									del instances['annotations'][ann_index2]['segmentation'][shape_index2]

						elif shape1 != shape2 and shape_index1 != shape_index2:
							# what we want to do here is split the annotations that could be very distant
							if not bboxContainsShape(bbox1, shape1) and bboxContainsShape(bbox2, shape2):
								# put shape1 into bbox2
								if len(instances['annotations'][ann_index1]['segmentation']) > 1:
									instances['annotations'][ann_index2]['segmentation'].append(shape1)
									if shape_index1 == len(instances['annotations'][ann_index1]['segmentation']):
										shape_index1 -= 1
									del instances['annotations'][ann_index1]['segmentation'][shape_index1]

							elif bboxContainsShape(bbox1, shape1) and not bboxContainsShape(bbox2, shape2):
								# puth shape 2 into bbox1
								if len(instances['annotations'][ann_index2]['segmentation']) > 1:
									instances['annotations'][ann_index1]['segmentation'].append(shape2)
									del instances['annotations'][ann_index2]['segmentation'][shape_index2]
							# elif not bboxContainsShape(bbox1, shape1) and not bboxContainsShape(bbox2, shape2):
							# 	if (len(instances['annotations'][ann_index1]['segmentation']) >
							# 		len(instances['annotations'][ann_index2]['segmentation'])
							# 		):
							# 		# put shape1 into bbox2
							# 		instances['annotations'][ann_index1]['segmentation'].append(shape1)
							# 		del instances['annotations'][ann_index1]['segmentation'][shape_index1]


				# no more duplicates (in theory but you never know for sure)

				if wrongbbox1 and not wrongbbox2:
					# let's move bbox1!
					counter1 += 1
					shape_bbox = maskBbox(mask1)
					# find the left top most

					logs['move_box'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox1': bbox2,
										'shapes_box': shape_bbox,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'wrong': 1
									})

					instances['annotations'][ann_index1]['bbox'][0] = shape_bbox[0]
					instances['annotations'][ann_index1]['bbox'][1] = shape_bbox[1]

					# move the annotations under the moved bbox
					# moveAnnotationsToBbox(shape_bbox,)
					
							
				elif not wrongbbox1 and wrongbbox2:
					# let's move bbox2!
					counter2 += 1
					shape_bbox = maskBbox(mask2)

					logs['move_box'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'shapes_box': shape_bbox,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'wrong': 2
									})

					
					instances['annotations'][ann_index2]['bbox'][0] = shape_bbox[0]
					instances['annotations'][ann_index2]['bbox'][1] = shape_bbox[1]
				elif wrongbbox1 and wrongbbox2:
					counter3 += 1
				elif not wrongbbox1 and not wrongbbox2:
					counter4 += 1
					# they are all still to analyze, because we only have analyzed the duplicates to remove them
					 # but usually in this case the smaller box is the better, so we'll
					# go for it and see the results
					#  to do this we'll

					

					if bboxContainsShape(bbox1, shape1) and not bboxContainsShape(bbox1, shape2):
						# we know shape 2 needs a new box
						if bboxShapeMargin(bbox1, shape1) < bboxShapeMargin(bbox2, shape1):
							# the shape 1 is more fit to bbox1, so we move bbox2
							shape_bbox = maskBbox(mask2)

							logs['move_box'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'shapes_box': shape_bbox,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'wrong': 0
									})

					
							instances['annotations'][ann_index2]['bbox'][0] = shape_bbox[0]
							instances['annotations'][ann_index2]['bbox'][1] = shape_bbox[1]
						else:
							# the shape 1 is more fit to bbox2, so we move bbox1
							shape_bbox = maskBbox(mask2)

							logs['move_box'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'shapes_box': shape_bbox,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'wrong': 0
									})

					
							instances['annotations'][ann_index1]['bbox'][0] = shape_bbox[0]
							instances['annotations'][ann_index1]['bbox'][1] = shape_bbox[1]

					elif not bboxContainsShape(bbox1, shape1) and bboxContainsShape(bbox1, shape2):
						# we know shape 1 needs a new box
						if bboxShapeMargin(bbox1, shape2) < bboxShapeMargin(bbox2, shape2):
							# the shape 2 is more fit to bbox1, so we move bbox2
							shape_bbox = maskBbox(mask1)

							logs['move_box'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'shapes_box': shape_bbox,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'wrong': 0
									})

					
							instances['annotations'][ann_index2]['bbox'][0] = shape_bbox[0]
							instances['annotations'][ann_index2]['bbox'][1] = shape_bbox[1]
						else:
							# the shape 2 is more fit to bbox2, so we move bbox1
							shape_bbox = maskBbox(mask1)

							logs['move_box'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'shapes_box': shape_bbox,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'wrong': 0
									})

					
							instances['annotations'][ann_index1]['bbox'][0] = shape_bbox[0]
							instances['annotations'][ann_index1]['bbox'][1] = shape_bbox[1]
					elif bboxContainsShape(bbox1, shape1) and bboxContainsShape(bbox1, shape2):
						# we use the rule of the most fitting!

						if bboxShapeMargin(bbox1, shape1) < bboxShapeMargin(bbox1, shape2):
							# we move the bbox2 to shape 2
							shape_bbox = maskBbox(mask2)

							logs['move_box'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'shapes_box': shape_bbox,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'wrong': 0
									})

					
							instances['annotations'][ann_index2]['bbox'][0] = shape_bbox[0]
							instances['annotations'][ann_index2]['bbox'][1] = shape_bbox[1]
						else:
							# we move bbox1 to shape 2
							shape_bbox = maskBbox(mask2)

							logs['move_box'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'shapes_box': shape_bbox,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'wrong': 0
									})

					
							instances['annotations'][ann_index1]['bbox'][0] = shape_bbox[0]
							instances['annotations'][ann_index1]['bbox'][1] = shape_bbox[1]

					# now using bbox2 as a reference
					if bboxContainsShape(bbox2, shape1) and not bboxContainsShape(bbox2, shape2):
						# we know shape 2 needs a new box
						if bboxShapeMargin(bbox1, shape1) < bboxShapeMargin(bbox2, shape1):
							# the shape 1 is more fit to bbox1, so we move bbox2
							shape_bbox = maskBbox(mask2)

							logs['move_box'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'shapes_box': shape_bbox,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'wrong': 0
									})

					
							instances['annotations'][ann_index2]['bbox'][0] = shape_bbox[0]
							instances['annotations'][ann_index2]['bbox'][1] = shape_bbox[1]
						else:
							# the shape 1 is more fit to bbox2, so we move bbox1
							shape_bbox = maskBbox(mask2)

							logs['move_box'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'shapes_box': shape_bbox,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'wrong': 0
									})

					
							instances['annotations'][ann_index1]['bbox'][0] = shape_bbox[0]
							instances['annotations'][ann_index1]['bbox'][1] = shape_bbox[1]

					elif not bboxContainsShape(bbox2, shape1) and bboxContainsShape(bbox2, shape2):
						# we know shape 1 needs a new box
						if bboxShapeMargin(bbox1, shape2) < bboxShapeMargin(bbox2, shape2):
							# the shape 2 is more fit to bbox1, so we move bbox2
							shape_bbox = maskBbox(mask1)

							logs['move_box'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'shapes_box': shape_bbox,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'wrong': 0
									})

					
							instances['annotations'][ann_index2]['bbox'][0] = shape_bbox[0]
							instances['annotations'][ann_index2]['bbox'][1] = shape_bbox[1]
						else:
							# the shape 2 is more fit to bbox2, so we move bbox1
							shape_bbox = maskBbox(mask1)

							logs['move_box'].append({
										'label': label1,
										'bbox1': bbox1,
										'bbox2': bbox2,
										'shapes_box': shape_bbox,
										'file_name': instances['images'][images_index[img_id]]['file_name'],
										'wrong': 0
									})

					
							instances['annotations'][ann_index1]['bbox'][0] = shape_bbox[0]
							instances['annotations'][ann_index1]['bbox'][1] = shape_bbox[1]





print(counter, counter1, counter2, counter3, counter4)

logs['invalid_boxes'] = []

# images_anns_indexes contains all the annotations for each image_id. 
# the key is the image_id, 
# the value is a list of the indexes of the annotations for that id in instances['annotations']
# i added categories here
images_anns_indexes = [ [ [] for j in range(14) ] for i in range(1115985) ]

for ann_index, ann in enumerate(instances['annotations']):
		img_id = ann['image_id']
		label = ann['category_id']
		images_anns_indexes[img_id][label].append(ann_index)

for img_id in img_ids:
	for label in range(1,14):

		# used to store and group lonely images
		mask_new = []

		for ann_index1 in images_anns_indexes[img_id][label]:
			ann1 = instances['annotations'][ann_index1]
			bbox1 = ann1['bbox']
			mask1 = ann1['segmentation']
			id1 = ann1['segmentation']

			if bbox1 == [400, 600, 400, 600]:
				logs['invalid_boxes'].append({
					'bbox':bbox1,
					'category_id':label,
					'segmentation': mask1,
					'id': id1,
					'image_id': img_id,
					'file_name': instances['images'][images_index[img_id]]['file_name']
				})

			for shape_index1, shape1 in enumerate(mask1):
				if not bboxContainsShape(bbox1, shape1):
					lonely = True
					# want to find if a shape is lonely
					for ann_index2 in images_anns_indexes[img_id][label]:
						ann2 = instances['annotations'][ann_index2]
						bbox2 = ann1['bbox']
						mask2 = ann1['segmentation']

						if ann_index1 != ann_index2 and bboxContainsShape(bbox2, shape1):
							lonely = False
							# moving the shape to the correct bbox
							instances['annotations'][ann_index2]['segmentation'].append(shape1)
							del instances['annotations'][ann_index1]['segmentation'][shape_index1]
							break
					if lonely:
						mask_new.append(shape1)
		
		bbox_new = maskBbox(mask_new)
		area_new = bbox_new[2] * bbox_new[3]
		id_new = 1000*area_new/(bbox_new[0]+1)
		instances['annotations'].append({
				'iscrowd':0,
				'category_id':label,
				'area': area_new,
				'segmentation': mask_new,
				'id': id_new,
				'image_id': img_id,
				'bbox': bbox_new
		})




print("Now writing logs in datasets/fix_logs folder..")

log_path = path + 'datasets/fix_logs/'
if not os.path.exists(log_path):
	os.makedirs(log_path)
with open(path + 'datasets/fix_logs/' + timestr +'.json', 'w') as outfile:
		json.dump(logs, outfile)


print("Now writing files..")
with open(ann_path + 'instances_all.json', 'w') as outfile:
		json.dump(instances, outfile)

print('\nArrange again the dataset using: maskrcnn-modanet datasets arrange')