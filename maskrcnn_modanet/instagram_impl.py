from instaloader import Instaloader

import getpass
import json
import lzma
import os
import platform
import re
import shutil
import string
import sys
import tempfile
from contextlib import contextmanager, suppress
from datetime import datetime, timezone
from functools import wraps
from hashlib import md5
from io import BytesIO
from pathlib import Path

import requests
import urllib3  # type: ignore

from instaloader.exceptions import *
from instaloader.instaloadercontext import InstaloaderContext

from typing import Any, Callable, Iterator, List, Optional, Set, Union

from instaloader.structures import (Highlight, JsonExportable, Post, PostLocation, Profile, Story, StoryItem,
						 save_structure_to_file, load_structure_from_file)


class ProfileURL(Profile):

	def get_posts(self, limit: Optional[int] = None, offset: Optional[int] = 0) -> Iterator[Post]:
		"""Retrieve all posts from a profile."""
		self._obtain_metadata()
		if limit:
			# yield from (Post(self._context, next(self._context.graphql_node_list("472f257a40c653c64c666ce877d59d2b",
			#                                                                 {'id': self.userid},
			#                                                                 'https://www.instagram.com/{0}/'.format(self.username),
			#                                                                 lambda d: d['data']['user']['edge_owner_to_timeline_media'],
			#                                                                 self._rhx_gis,
			#                                                                 self._metadata('edge_owner_to_timeline_media'))), self)
			#             for i in range(min(limit) )

			posts = []
			for node_index, node in enumerate(self._context.graphql_node_list("472f257a40c653c64c666ce877d59d2b",
																		{'id': self.userid},
																		'https://www.instagram.com/{0}/'.format(self.username),
																		lambda d: d['data']['user']['edge_owner_to_timeline_media'],
																		self._rhx_gis,
																		self._metadata('edge_owner_to_timeline_media'))):
				if node_index < offset:
					continue
				elif node_index == limit + offset:
					break
				else:
					posts.append(Post(self._context, node, self))
			yield from posts
		else:
			yield from (Post(self._context, node, self) for node in
					self._context.graphql_node_list("472f257a40c653c64c666ce877d59d2b",
													{'id': self.userid},
													'https://www.instagram.com/{0}/'.format(self.username),
													lambda d: d['data']['user']['edge_owner_to_timeline_media'],
													self._rhx_gis,
													self._metadata('edge_owner_to_timeline_media')))

class InstaloaderURL(Instaloader):

	def check_profile_id(self, profile_name: str) -> Profile:
		"""
		Consult locally stored ID of profile with given name, check whether ID matches and whether name
		has changed and return current name of the profile, and store ID of profile.

		:param profile_name: Profile name
		:return: Instance of current profile
		"""
		profile = None
		with suppress(ProfileNotExistsException):
			profile = ProfileURL.from_username(self.context, profile_name)
		profile_exists = profile is not None
		id_filename = self._get_id_filename(profile_name)
		try:
			with open(id_filename, 'rb') as id_file:
				profile_id = int(id_file.read())
			if (not profile_exists) or \
					(profile_id != profile.userid):
				if profile_exists:
					self.context.log("Profile {0} does not match the stored unique ID {1}.".format(profile_name,
																								   profile_id))
				else:
					self.context.log("Trying to find profile {0} using its unique ID {1}.".format(profile_name,
																								  profile_id))
				profile_from_id = Profile.from_id(self.context, profile_id)
				newname = profile_from_id.username
				self.context.log("Profile {0} has changed its name to {1}.".format(profile_name, newname))
				if ((format_string_contains_key(self.dirname_pattern, 'profile') or
					 format_string_contains_key(self.dirname_pattern, 'target'))):
					os.rename(self.dirname_pattern.format(profile=profile_name.lower(),
														  target=profile_name.lower()),
							  self.dirname_pattern.format(profile=newname.lower(),
														  target=newname.lower()))
				else:
					os.rename('{0}/{1}_id'.format(self.dirname_pattern.format(), profile_name.lower()),
							  '{0}/{1}_id'.format(self.dirname_pattern.format(), newname.lower()))
				return profile_from_id
			return profile
		except (FileNotFoundError, ValueError):
			pass
		if profile_exists:
			self.save_profile_id(profile)
			return profile
		raise ProfileNotExistsException("Profile {0} does not exist.".format(profile_name))

	def profile_posts_urls(self, profile_name: Union[str, Profile],
						 profile_pic: bool = False, profile_pic_only: bool = False,
						 fast_update: bool = False,
						 download_stories: bool = False, download_stories_only: bool = False,
						 download_tagged: bool = False, download_tagged_only: bool = False,
						 post_filter: Optional[Callable[[Post], bool]] = None,
						 storyitem_filter: Optional[Callable[[StoryItem], bool]] = None,
						 limit: Optional[int] = None,
						 offset: Optional[int] = 0) -> List[str]:
		"""Download one profile

		.. deprecated:: 4.1
		   Use :meth:`Instaloader.download_profiles`.
		"""

		# Get profile main page json
		# check if profile does exist or name has changed since last download
		# and update name and json data if necessary
		if isinstance(profile_name, str):
			profile = self.check_profile_id(profile_name.lower())
		else:
			profile = profile_name

		profile_name = profile.username

		url_pics = []

		# Save metadata as JSON if desired.
		if self.save_metadata is not False:
			json_filename = '{0}/{1}_{2}'.format(self.dirname_pattern.format(profile=profile_name, target=profile_name),
												 profile_name, profile.userid)
			self.save_metadata_json(json_filename, profile)

		if self.context.is_logged_in and profile.has_blocked_viewer and not profile.is_private:
			# raising ProfileNotExistsException invokes "trying again anonymously" logic
			raise ProfileNotExistsException("Profile {} has blocked you".format(profile_name))

		# Download profile picture
		if profile_pic or profile_pic_only:
			with self.context.error_catcher('Download profile picture of {}'.format(profile_name)):
				# self.download_profilepic(profile)
				pass
		if profile_pic_only:
			return

		# Catch some errors
		if profile.is_private:
			if not self.context.is_logged_in:
				raise LoginRequiredException("profile %s requires login" % profile_name)
			if not profile.followed_by_viewer and \
					self.context.username != profile.username:
				raise PrivateProfileNotFollowedException("Profile %s: private but not followed." % profile_name)
		else:
			if self.context.is_logged_in and not (download_stories or download_stories_only):
				self.context.log("profile %s could also be downloaded anonymously." % profile_name)

		# Download stories, if requested
		if download_stories or download_stories_only:
			if profile.has_viewable_story:
				with self.context.error_catcher("Download stories of {}".format(profile_name)):
					# self.download_stories(userids=[profile.userid], filename_target=profile_name,
										  # fast_update=fast_update, storyitem_filter=storyitem_filter)
					pass
			else:
				self.context.log("{} does not have any stories.".format(profile_name))
		if download_stories_only:
			return

		# Download tagged, if requested
		if download_tagged or download_tagged_only:
			with self.context.error_catcher('Download tagged of {}'.format(profile_name)):
				# self.download_tagged(profile, fast_update=fast_update, post_filter=post_filter)
				pass
		if download_tagged_only:
			return

		# Iterate over pictures and download them
		self.context.log("Retrieving posts from profile {}.".format(profile_name))
		totalcount = profile.mediacount
		count = 1
		for post in profile.get_posts(limit=limit, offset=offset):
			self.context.log("[%3i/%3i] " % (count, totalcount), end="", flush=True)
			count += 1
			if post_filter is not None and not post_filter(post):
				self.context.log('<skipped>')
				continue
			with self.context.error_catcher('Download URL profile {}'.format(profile_name)):
				downloaded, url_pics_post = self.url_post(post, target=profile_name)
				for url_pic_post in url_pics_post:
					url_pics.append(url_pic_post)

				if fast_update and not downloaded:
					break

		return url_pics

	def url_post(self, post: Post, target: Union[str, Path]) -> (bool, List[str]):
		"""
		Get URL of one instagram post node.

		:param post: Post to get URL.
		:param target: Target name, i.e. profile name, #hashtag, :feed; for filename.
		:return: True if something was downloaded, False otherwise, i.e. file was already there
		"""

		# Download the image(s) / video thumbnail and videos within sidecars if desired
		downloaded = True
		url_pics = []
		if self.download_pictures:
			if post.typename == 'GraphSidecar':
				edge_number = 1
				for sidecar_node in post.get_sidecar_nodes():
					# Download picture or video thumbnail
					if not sidecar_node.is_video or self.download_video_thumbnails is True:
						downloaded &= True
						url_pics.append(sidecar_node.display_url)
					# Additionally download video if available and desired
					if sidecar_node.is_video and self.download_videos is True:
						# downloaded &= self.download_pic(filename=filename, url=sidecar_node.video_url,
						#                                 mtime=post.date_local, filename_suffix=str(edge_number))
						pass
					edge_number += 1
			elif post.typename == 'GraphImage':
				downloaded = True
				url_pics.append(post.url)
			elif post.typename == 'GraphVideo':
				if self.download_video_thumbnails is True:
					# downloaded = self.download_pic(filename=filename, url=post.url, mtime=post.date_local)
					pass
			else:
				self.context.error("Warning: {0} has unknown typename: {1}".format(post, post.typename))

		# # Save caption if desired
		# metadata_string = _ArbitraryItemFormatter(post).format(self.post_metadata_txt_pattern).strip()
		# if metadata_string:
		#     self.save_caption(filename=filename, mtime=post.date_local, caption=metadata_string)

		# Download video if desired
		if post.is_video and self.download_videos is True:
			# downloaded &= self.download_pic(filename=filename, url=post.video_url, mtime=post.date_local)
			pass

		# Download geotags if desired
		if self.download_geotags and post.location:
			# self.save_location(filename, post.location, post.date_local)
			pass

		# Update comments if desired
		if self.download_comments is True:
			# self.update_comments(filename=filename, post=post)
			pass

		# Save metadata as JSON if desired.
		if self.save_metadata is not False:
			# self.save_metadata_json(filename, post)
			pass

		self.context.log()
		return downloaded, url_pics


def viewImageFromURL(url_pic):
	import requests, cv2
	from keras_retinanet.utils.image import read_image_bgr
	import matplotlib.pyplot as plt

	r = requests.get(url_pic, allow_redirects=True)
	image = read_image_bgr(BytesIO(r.content))

	# copy to draw on
	draw = image.copy()
	
	draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)


	plt.figure(figsize=(15, 15))
	plt.axis('off')
	plt.imshow(draw)
	plt.show()


def getImageFromURL(url_pic, draw=False):
	''' The image is the one that will be processed, the draw is the one to be shown '''
	import requests, cv2
	from keras_retinanet.utils.image import read_image_bgr

	r = requests.get(url_pic, allow_redirects=True)
	image = read_image_bgr(BytesIO(r.content))

	

	if draw:
		# copy to draw on
		draw = image.copy()
		
		draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

		return image, draw
	else:
		return image



def getImageFromFilePath(img_path, draw=False):
	''' The image is the one that will be processed, the draw is the one to be shown '''
	import requests, cv2
	from keras_retinanet.utils.image import read_image_bgr

	image = read_image_bgr(img_path)

	

	if draw:
		# copy to draw on
		draw = image.copy()
		
		draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

		return image, draw
	else:
		return image



def instagramImpl(profile, limit=None, offset=0, process_images=True, profile_stats=True, choice=None, restore_result=False):      
	from maskrcnn_modanet.instagram_impl import InstaloaderURL
	import matplotlib.pyplot as plt
	import cv2

	import time

	import json
	import codecs
	import os

	import numpy as np

	from maskrcnn_modanet.cli import validators

	from PIL import Image



	with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
		savedvars = json.load(f)
	path = savedvars['datapath']

	img_path = path + "datasets/coco/images/"
	ann_path = path + "datasets/coco/annotations/"
	snp_path = path + "results/snapshots"


	timestr = time.strftime("%Y%m%d-%H%M%S")

	profile_path = path + 'results/instagram/'+ profile + '/'

	save_images_path = profile_path + 'images/'

	save_segments_path = profile_path + 'segments/'

	log_path = profile_path + timestr + '.txt'


	from instaloader import (InstaloaderException, InvalidArgumentException, Post, Profile, ProfileNotExistsException,
			   StoryItem, __version__, load_structure_from_file, TwoFactorAuthRequiredException,
			   BadCredentialsException)
	

	if not restore_result:

		instaloader = InstaloaderURL(dirname_pattern=path+'/results/instagram/{target}',download_pictures=True, download_videos=False, download_video_thumbnails=False,
								 download_geotags=False,
								 download_comments=False, save_metadata=False,
							)

		target = profile

		profile = instaloader.check_profile_id(target)

		log_file = open(log_path, 'w+')

		
		if os.path.exists(save_images_path):
			for the_file in os.listdir(save_images_path):
				file_path = os.path.join(save_images_path, the_file)
				try:
					if os.path.isfile(file_path):
						os.unlink(file_path)
					#elif os.path.isdir(file_path): shutil.rmtree(file_path)
				except Exception as e:
					print(e)

		save_images_path = validators.check_if_folder_exists(None, None, save_images_path)

		print(profile)

		url_pics = instaloader.profile_posts_urls(profile, limit=limit, offset=offset)

		# print(url_pics)

		pics = []

		# for url_pic in url_pics:


		if process_images and not profile_stats:
			from maskrcnn_modanet.processimages import loadModel, main

			model, labels_to_names = loadModel(model_type='default')
		elif process_images and profile_stats:
			from maskrcnn_modanet.processimages import loadModel

			model, labels_to_names = loadModel(model_type='coco')

			print('Now looking for images with only one person in the image..')

			
		
		from keras_retinanet.utils.image import read_image_bgr
		import requests
		from io import BytesIO

		url_pics_person = []

		pic_index = 0
		for url_pic in url_pics:
			if not process_images:
				viewImageFromURL(url_pic)
			elif process_images and not profile_stats:
				# image, draw = getImageFromURL(url_pic, draw=True)

				# img_anns = apply_mask(model, image, threshold_score=0.5)

				# for img_ann in img_anns:
				# 	if img_ann['category'] == 'person':


				main(proc_img_path=None, proc_img_url=url_pic, all_set=False, save_images_path=None, model_path=None, 
					segments=False, annotations=False, threshold_score=0.5, limit=None, model=model, labels_to_names=labels_to_names)
			elif process_images and profile_stats:
				from maskrcnn_modanet.processimages import apply_mask

				print(pic_index, end=' ')
				print(pic_index, end=' ', file=log_file)
				print(url_pic, file=log_file)

				try:
					image, draw = getImageFromURL(url_pic, draw=True)
				except Exception:
					print('Image ', pic_index, 'failed to download. Url tried below:\n' + url_pic + '\n\n Continuing to next image..')
					print('Image ', pic_index, 'failed to download. Url tried below:\n' + url_pic + '\n\n Continuing to next image..', file=log_file)
					continue

				image_area = len(image) * len(image[0])

				pic_index += 1

				img_anns = apply_mask(model, image, draw=draw, labels_to_names=labels_to_names, image_segments=False)

				one_person = 0
				for img_ann in img_anns:
					if img_ann['category'] == 'person' and img_ann['bbox'][2] * img_ann['bbox'][3] >= 0.1 * image_area:
						one_person += 1
						print(one_person, 'person that covers ', round(img_ann['bbox'][2] * img_ann['bbox'][3] / image_area * 100),'%  of the image found in this photo', file=log_file)
					if one_person > 1:
						# we only select images with only one person that covers an area greater than 10% of the image
						print('Too many people found in this photo', file=log_file)
						one_person = 0
						break

				if one_person:
					# # show the image
					# plt.figure(figsize=(15, 15))
					# plt.axis('off')
					# plt.imshow(draw)
					# plt.show()

					# add the pic to the new urls
					url_pics_person.append([pic_index, url_pic])

		if process_images and profile_stats:
			print('We\'ve now selected the images that are probably the ones with only the person who owns this account.')
			if not choice:
				choice = ''
			while choice not in ['i', 's']:
				choice = input('Do you want to see the images processed or to see some stats? Type \'i\' for image, \'s\' for stats: ')

			# now let's switch to ModaNet and look into the image

			model, labels_to_names = loadModel(model_type='default')

			for label_index in labels_to_names:
				segment_label_path = save_segments_path + labels_to_names[label_index] + '/'

				# remove all previous segments saved

				if os.path.exists(segment_label_path):
					for the_file in os.listdir(segment_label_path):
						file_path = os.path.join(segment_label_path, the_file)
						try:
							if os.path.isfile(file_path):
								os.unlink(file_path)
							#elif os.path.isdir(file_path): shutil.rmtree(file_path)
						except Exception as e:
							print(e)

				segment_label_path = validators.check_if_folder_exists(None, None, segment_label_path)

			labels_images = {}

			for pic_index, url_pic in url_pics_person:
				image, draw = getImageFromURL(url_pic, draw=True)

				print(pic_index, end=' ')
				print(pic_index, end=' ', file=log_file)
				print(url_pic, file=log_file)

				

				if choice == 'i':
					img_anns = apply_mask(model, image, draw=draw, labels_to_names=labels_to_names, image_segments=False)
					# show the image
					plt.figure(figsize=(15, 15), num=str(pic_index))
					plt.axis('off')
					plt.imshow(draw)

					plt.show()
				elif choice == 's':
					img_anns = apply_mask(model, image, draw=draw, labels_to_names=labels_to_names, image_segments=True)

					# save the images for easy retrieval
					# plt.figure(num=str(pic_index), dpi=400)
					# plt.axis('off')
					# plt.imshow(draw)
					# plt.savefig(save_images_path + str(pic_index) + '.png')
					# plt.close()
					processed_image = Image.fromarray(draw, 'RGB')
					processed_image.save(save_images_path + str(pic_index) + '.png')
					del processed_image

					# let's count
					labels_images[pic_index] = {}
					for label_index in labels_to_names:
						labels_images[pic_index][labels_to_names[label_index]] = []

					for img_ann in img_anns:
						save_segment_path = save_segments_path + img_ann['category'] + '/' + str(pic_index) + '_.png'
						segment_counter = 1
						while os.path.isfile(save_segment_path):
							save_segment_path = "_".join(save_segment_path.split("_")[:-1]) + "_" + str(segment_counter) + '.png'
							segment_counter += 1
						segment = Image.fromarray(img_ann.pop('segment'), 'RGB')
						segment.save(save_segment_path)
						del segment
						img_ann['segment'] = save_segment_path
						labels_images[pic_index][img_ann['category']].append(img_ann)

			if choice == 's':
				results = {
					'url_pics': url_pics,
					'url_pics_person': url_pics_person,
					'labels_to_names': labels_to_names
				}

				print('Saving annotations results for easy recovery.. Use -r option later')
				with open(profile_path + 'results.json', 'w') as outfile:
					json.dump(results, outfile)
				print('Now saving annotations..')
				with open(profile_path + 'labels_images.json', 'wb') as outfile:
					np.save(outfile, labels_images)


	elif restore_result:
		log_file = open(log_path, 'w+')
		
		print('Restoring results..')
		with open(profile_path + 'results.json') as f:
			results = json.load(f)
		print('Restoring annotations..')
		with open(profile_path + 'labels_images.json', 'rb') as f:
			labels_images = np.load(f, allow_pickle=True)[()]
			# credit goes to https://stackoverflow.com/questions/30811918/saving-dictionary-of-numpy-arrays

		url_pics = results['url_pics']
		url_pics_person = results['url_pics_person']
		labels_to_names = results['labels_to_names']

		print('We\'ve now recovered the images that are probably the ones with only the person who owns this account, processed to look for apparel and clothing items.')
		if not choice:
			choice = ''
		while choice not in ['i', 's']:
			choice = input('Do you want to see the images processed or to see some stats? Type \'i\' for image, \'s\' for stats: ')

	if process_images and profile_stats:
		if choice == 'i' and restore_result:
			for pic_index, url_pic in url_pics_person:
				image, draw = getImageFromFilePath(save_images_path + str(pic_index) + '.png', draw=True)
				plt.figure(figsize=(9, 9), num=str(pic_index))
				plt.axis('off')
				plt.imshow(draw)
				plt.show()



		elif choice == 's':
			print('I will now show you all the stats I can think of:')
			print('I will now show you all the stats I can think of:', file=log_file)
			print('Total images:', len(url_pics), 'Images with one person: ', len(url_pics_person))
			print('Total images:', len(url_pics), 'Images with one person: ', len(url_pics_person), file=log_file)
			print(round(len(url_pics_person)/len(url_pics)*100, 1), '%  of the images contain only one main subject (probably the account owner)')
			print(round(len(url_pics_person)/len(url_pics)*100, 1), '%  of the images contain only one main subject (probably the account owner)', file=log_file)

			# for label_index in labels_to_names:
			# 	label = label[label_index]
			# how many of each label
			len_labels = {}
			
			for label_index in labels_to_names:
				len_labels[labels_to_names[label_index]] = 0
				
			for pic_index in labels_images:
				for label in labels_images[pic_index]:
					len_labels[label] += len(labels_images[pic_index][label])
			sum_len_labels = sum(len_labels[i] for i in len_labels)
			print('There are ', sum_len_labels, ' total instances of labels')
			print('There are ', sum_len_labels, ' total instances of labels', file=log_file)
			print(f'Instances of labels per image: {sum_len_labels/len(url_pics_person):4.2f}')
			print(f'Instances of labels per image: {sum_len_labels/len(url_pics_person):4.2f}', file=log_file)
			for label in len_labels:

				perc_label = len_labels[label]/sum_len_labels
				avg_label = sum(len(labels_images[pic_index][label]) for pic_index in labels_images)/len(labels_images)
				print(f'Label: {label:15} Perc: {len_labels[label]/sum_len_labels:>6.1%} | Per Image: Avg: {len_labels[label]/len(labels_images):>4.2f} Max: {max(len(labels_images[pic_index][label]) for pic_index in labels_images)}')
				print(f'Label: {label:15} Perc: {len_labels[label]/sum_len_labels:>6.1%} | Per Image: Avg: {len_labels[label]/len(labels_images):>4.2f} Max: {max(len(labels_images[pic_index][label]) for pic_index in labels_images)}', file=log_file)

			label_again = True
			while label_again:
				label = ' '
				while label not in len_labels and label != '':
					label = input('Insert a label to see its instances!\nUseful if you want to see which shoes your favourite instagram user has.\nYou can see the labels above. Press enter to abort: ')
				if label == '':
					label_again = False
					break
				segments = [img_ann['segment'] for pic_index in labels_images
												for img_ann in labels_images[pic_index][label] ]
				if len(segments) > 0:
					print('There are ', len(segments), ' results. Tell me the start and the end, as if you were slicing a Python array')
					print('You can also find the results in the folder:\n' + "/".join(segments[0].split("/")[:-1]))
					from_i = input('Start: ')
					if from_i == '':
						from_i = None
					else:
						from_i = int(from_i)
					to_i = input('End: ')
					if to_i == '':
						to_i = None
					else:
						to_i = int(to_i)

					

					for segment_path in segments[from_i:to_i]:
						img = Image.open(segment_path)
						img.show(title=segment_path.split('/')[-1])
						del img
				else:
					print('There are no segments to show for this label.\n')
					
					# plt.figure(figsize=(5, 5), num=str(pic_index), dpi=400)
					# plt.axis('off')
					# plt.imshow(segment)
					# plt.show()




	print('You can find the logs as a txt file in:\n' + log_path)

	log_file.close()
	
