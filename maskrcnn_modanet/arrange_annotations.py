import json
import os

with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
	savedvars = json.load(f)
path = savedvars['datapath']

fast_download = savedvars['fast_download'] == 'True'

import copy

import random



ann_path = path + "datasets/coco/annotations/"
ann_orig_path = path + 'datasets/modanet/annotations/'

sets_names = ['train', 'val', 'test']

if not os.path.isfile(ann_path + 'instances_all.json'):
	# copy the modanet instances to the annotations folder
	print('Copying annotations from the original path')
	with open(ann_orig_path + 'modanet2018_instances_' + sets_names[0] + '.json') as f:
		instances = json.load(f)
	with open(ann_path + 'instances_all.json', 'w') as outfile:
		json.dump(instances, outfile)

print('Now arranging annotations. Just delete the file \'instances_all.json\' and rerun this command, if you want to restore it to the original one.')
print()

# now asking variables, if not already saved
if savedvars['percentagetrain'] == None:
	savedvars['seed'] = input('Random images selection seed (insert a number of your choice): ')
	savedvars['percentagetrain'] = input('Train Annotations Set Percentage: ')
	savedvars['percentageval'] = input('Val Annotations Set Percentage: ')
	savedvars['percentagetest'] = input('Test Annotations Set Percentage: ')

	# now saving them
	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json', 'w') as outfile:
		json.dump(savedvars, outfile)


sets_percentages = [int(savedvars['percentagetrain']), int(savedvars['percentageval']), int(savedvars['percentagetest'])]
random.seed(int(savedvars['seed']))


print("Doing " + str([str(p) + '% ' + n for p, n in zip(sets_percentages, sets_names)]))
print('You can always change them later by typing: maskrcnn-modanet savedvars edit [variable name] [variable value]')
print('You can check the names of the variables by typing: maskrcnn-modanet savedvars show')


with open(ann_path + 'instances_all.json') as f:
    instances = json.load(f)

print("Annotations:" + str(len(instances['annotations'])))
print("Images:" + str(len(instances['images'])))

train_ann = {
	'year': instances['year'],
	'categories': instances['categories'],
	'annotations': [],
	'licenses': instances['licenses'],
	'type': instances['type'],
	'info': instances['info'],
	'images': []
}
val_ann = copy.deepcopy(train_ann)
test_ann = copy.deepcopy(train_ann)

if sum(sets_percentages) != 100:
	print("Values not valid, doing 80% train, 10 val and 10 test! Please update your sets percentages")
	sets_percentages = [80, 10, 10]

split_percs = [0]
for perc in sets_percentages:
	#make it cumulative
	last_perc = split_percs.pop()
	split_percs.extend([last_perc + perc] * 2)
split_percs.pop()
# now is [80, 90, 100]


#cat_split_percs = [split_percs for i in range(len(instances['categories']) + 1)]
# has the percentages of cumulative probability for each category (will be modified later)

images_anns = [ [0] * 1115985 for i in range(len(instances['categories']) + 1)] #categories start from one
# has the images referenced by the annotations for each category, with key the id and value how many annotations has the image of that category

cat_anns = [ [0, 0, 0] for i in range(len(instances['categories']) + 1) ]
# has [category][set (train{0}, val{1}, test{2})] and as value the number of annotations in that set for that category. to be filled

images_set = [None] * 1115985
# has as key, image id, as value, (train{0}, val{1}, test{2}). used for faster recovering of this info

for ann in instances['annotations']:
	images_anns[ann['category_id']][ann['image_id']] += 1

print("Annotations categories for each image recorded")

sum_images_anns = [ sum(images_anns_cat) for images_anns_cat in images_anns ]


# now that I know what annotations images contain, apply probability
for img in instances['images']:
	img_id = img['id']
	p = random.random() * 100
	if p < split_percs[0]:
		train_ann['images'].append(img)
		images_set[img_id] = 0
		for cat_id in range(1, len(instances['categories']) + 1): # for each category
			cat_anns[cat_id][0] += images_anns[cat_id][img_id] # record how many annotations have been added to a set

	elif split_percs[0] <= p < split_percs[1]:
		val_ann['images'].append(img)
		images_set[img_id] = 1
		for cat_id in range(1, len(instances['categories']) + 1): # for each category
			cat_anns[cat_id][1] += images_anns[cat_id][img_id] # record how many annotations have been added to a set
			
	elif p <= split_percs[2]:
		test_ann['images'].append(img)
		images_set[img_id] = 2
		for cat_id in range(1, len(instances['categories']) + 1): # for each category
			cat_anns[cat_id][2] += images_anns[cat_id][img_id] # record how many annotations have been added to a set
			

for cat_id in range(1, len(cat_anns)):
	print("Category ID: " + str(cat_id) + "\tCat Anns: " + str(sum(cat_anns[cat_id])) + 
		"\tCat Percs:" + str([i / float(sum(cat_anns[cat_id])) * 100 for i in cat_anns[cat_id]]))



print()
print("Adding annotations..")
for ann in instances['annotations']:
	# add the annotations to the correct sets
	img_id = ann['image_id']
	if images_set[img_id] == 0:
		train_ann['annotations'].append(ann)
	elif images_set[img_id] == 1:
		val_ann['annotations'].append(ann)
	elif images_set[img_id] == 2:
		test_ann['annotations'].append(ann)
print()
print("Result sum annotations:" + str(sum([len(train_ann['annotations']), len(val_ann['annotations']), len(test_ann['annotations'])])))
print("Result sum images:" + str(sum([len(train_ann['images']), len(val_ann['images']), len(test_ann['images'])])))
print()
print("Now writing files..")
with open(ann_path + 'instances_train.json', 'w') as outfile:
	json.dump(train_ann, outfile)

with open(ann_path + 'instances_val.json', 'w') as outfile:
	json.dump(val_ann, outfile)

with open(ann_path + 'instances_test.json', 'w') as outfile:
	json.dump(test_ann, outfile)

print('\nNow you can train using: maskrcnn-modanet train')

print('\nOr you can fix the dataset using: maskrcnn-modanet datasets fix')

if fast_download:
	print('Your dataset is already fixed anyway, since you fast-downloaded it.')