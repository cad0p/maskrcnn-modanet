import json
import os

with open(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json') as f:
	print(os.path.expanduser('~')+ '/.maskrcnn-modanet/' + 'savedvars.json')
	savedvars = json.load(f)
path = savedvars['datapath']

fast_download = savedvars['fast_download'] == 'True'

if fast_download:
    print('Images already arranged!')
else:

    import io
    import lmdb
    import sqlite3
    import pandas as pd
    from PIL import Image
    import sqlalchemy

    # name of the set we are getting the annotations from. in the case of modanet, the set containing all info is the train one.
    set_name = 'train'


    img_orig_path = path + 'datasets/paperdoll/data/chictopia/'
    ann_orig_path = path + 'datasets/modanet/annotations/'
    img_path = path + "datasets/coco/images/"
    ann_path = path + "datasets/coco/annotations/"

    print("Img coming from : " + img_orig_path)
    print("Ann coming from : " + ann_orig_path)
    print("Img are now here: " + img_path)
    print("Ann are now here: " + ann_path)


    print(img_orig_path + 'chictopia.sqlite3')
    db = sqlite3.connect(img_orig_path + 'chictopia.sqlite3')

    with open(ann_orig_path + 'modanet2018_instances_' + set_name + '.json') as f:
        instances = json.load(f)

    #instances['images'][i]['id']
    photosIDs = []
    photosFILE_NAMEs = [None] * 1115985 #1097474
    for instance in instances['images']:
        photosIDs.append(instance['id'])
        photosFILE_NAMEs[instance['id']] = instance['file_name']
    #import ipdb; ipdb.set_trace()
    #photosIDs = [100014, 100040]
    photosIDsString = ''
    for photoID in photosIDs:
        photosIDsString += str(photoID) + ', '
    photosIDsString = photosIDsString[:-2]
    #print(photosIDsString)

    sql = str(sqlalchemy.text("""
        SELECT
            *,
            'http://images2.chictopia.com/' || path AS url
        FROM photos
        WHERE photos.post_id IS NOT NULL AND file_file_size IS NOT NULL
            AND photos.id IN ( %s )
    """ % photosIDsString))

    photos = pd.read_sql(sql, con=db)
    print('photos = %d' % (len(photos)))
    photos.head()

    class PhotoData(object):
        def __init__(self, path):
            self.env = lmdb.open(
                path, map_size=2**36, readonly=True, lock=False
            )
            
        def __iter__(self):
            with self.env.begin() as t:
                with t.cursor() as c:
                    for key, value in c:
                        yield key, value
            
        def __getitem__(self, index):
            key = str(index).encode('ascii')
            with self.env.begin() as t:
                data = t.get(key)
            if not data:
                return None
            with io.BytesIO(data) as f:
                image = Image.open(f)
                image.load()
                return image
            
        def __len__(self):
            return self.env.stat()['entries']

    photo_data = PhotoData(img_orig_path + 'photos.lmdb')
    print("Total # of photos (also the ones without annotations) is " + str(len(photo_data)))
    print()
    print('Copying photos to the new folder (just for the first run)')
    from progressbar import ProgressBar
    pbar = ProgressBar()
    for i in pbar(range(len(photosIDs))):
        photo = photos.iloc[i]
        if not os.path.isfile(img_path + photosFILE_NAMEs[photo.id]):
        	photo_data[photo.id].save(img_path + photosFILE_NAMEs[photo.id])

print()
print()