#!/bin/bash

cd
mkdir .maskrcnn-modanet
cd .maskrcnn-modanet
pwd
echo "saving your path location"

PATH1=$1
echo $PATH1

cd $PATH1

mkdir datasets
cd datasets


# download images dataset
git clone https://github.com/kyamagu/paperdoll
pwd
cd paperdoll/data/chictopia
pwd

if [ ! -d "./photos.lmdb" ]
then
	echo "If you already have the 40GB file lying around, you can stop the download by closing this program now,"
	echo "putting the photos.lmdb file into ./datasets/paperdoll/data/chictopia"
	echo "and then restarting this program again so that it thinks it's already downloaded (did you?)"
	echo "or you could just wait a few hours of your precious time here.."
	wget http://vision.is.tohoku.ac.jp/chictopia2/photos.lmdb.tar
	tar xf photos.lmdb.tar
	if [ -d "./photos.lmdb" ]
	then
		rm photos.lmdb.tar
	else
		echo "install tar and run again this command!"
		exit 1
	fi
else echo "photos database already downloaded!"
fi

gunzip -c chictopia.sql.gz | sqlite3 chictopia.sqlite3
if [ -f "./chictopia.sqlite3" ]
then
	rm chictopia.sql.gz
else
	echo "install gunzip and sqlite3 and run again this command!"
	exit 1
fi

cd ..
cd ..
cd ..
pwd
text="\n
now downloading modanet annotations\n
					\t\t\ttaken from here:\n
					\t\t\thttps://github.com/eBay/modanet"

echo $text

# download images annotations
git clone https://github.com/eBay/modanet.git


mkdir coco #this will be our dataset final folder
cd coco
mkdir images
mkdir annotations

cd ..
cd .. #now in main folder
mkdir results
cd results
pwd
mkdir snapshots
mkdir processedimages
mkdir logs

cd processedimages
pwd
mkdir images
mkdir imagesegments
mkdir annotations


# does not show folders named lib (which clutter the graph)
tree -d $PATH1 -I lib --matchdirs


