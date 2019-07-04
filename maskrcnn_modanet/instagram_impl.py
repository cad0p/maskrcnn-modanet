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

class InstaloaderURL(Instaloader):

    def profile_posts_urls(self, profile_name: Union[str, Profile],
                         profile_pic: bool = False, profile_pic_only: bool = False,
                         fast_update: bool = False,
                         download_stories: bool = False, download_stories_only: bool = False,
                         download_tagged: bool = False, download_tagged_only: bool = False,
                         post_filter: Optional[Callable[[Post], bool]] = None,
                         storyitem_filter: Optional[Callable[[StoryItem], bool]] = None) -> List[str]:
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
        for post in profile.get_posts():
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




def instagramImpl(profile):
	from maskrcnn_modanet.instagram_impl import InstaloaderURL
	import matplotlib.pyplot as plt
	import cv2

	from instaloader import (InstaloaderException, InvalidArgumentException, Post, Profile, ProfileNotExistsException,
               StoryItem, __version__, load_structure_from_file, TwoFactorAuthRequiredException,
               BadCredentialsException)

	instaloader = InstaloaderURL(download_pictures=True, download_videos=False, download_video_thumbnails=False,
                             download_geotags=False,
                             download_comments=False, save_metadata=False,
                        )

	target = profile

	profile = instaloader.check_profile_id(target)

	print(profile)

	url_pics = instaloader.profile_posts_urls(profile)
	
	from keras_retinanet.utils.image import read_image_bgr
	import requests
	from io import BytesIO
	for url_pic in url_pics:
		r = requests.get(url_pic, allow_redirects=True)
		image = read_image_bgr(BytesIO(r.content))

		# copy to draw on
		draw = image.copy()
		
		draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)


		plt.figure(figsize=(15, 15))
		plt.axis('off')
		plt.imshow(draw)
		plt.show()