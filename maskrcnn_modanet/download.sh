#!/bin/bash

git lfs install

cd
mkdir .maskrcnn-modanet
cd .maskrcnn-modanet
pwd
echo "saving your path location"

PATH1=$1
echo $PATH1

FAST=$2
echo "fast download:"
echo $FAST

cd $PATH1

mkdir datasets
cd datasets

if [ ! "$FAST" == "True" ]
then
	
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
		wget -c http://vision.is.tohoku.ac.jp/chictopia2/photos.lmdb.tar
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

	echo "unzipping database.."
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

else
	echo "Skipping downloading PaperDoll"
fi

pwd

text="\n
now downloading modanet annotations\n
					\t\t\ttaken from here:\n
					\t\t\thttps://github.com/eBay/modanet"

echo $text

# download images annotations
git clone https://github.com/eBay/modanet.git

cd modanet
cd annotations

wget -O modanet2018_instances_train.json https://github.com/cad0p/maskrcnn-modanet/releases/download/v1.0.3/modanet2018_instances_train.json

wget -O modanet2018_instances_val.json https://github.com/cad0p/maskrcnn-modanet/releases/download/v1.0.3/modanet2018_instances_val.json

cd ..
cd ..


mkdir coco #this will be our dataset final folder
cd coco

mkdir annotations

if [ "$FAST" == "True" ]
then
	pwd
	echo "downloading the images folder.. (2 GB)"
	if [ ! -d "./images" ]
	then
		wget -c https://github.com/cad0p/maskrcnn-modanet/releases/download/v0.9/images.zip
		echo "unzipping.."
		unzip -q images.zip
		if [ -d "./images" ]
		then
			rm images.zip
		else
			echo "could not unzip file. run command again"
			exit 1
		fi
	else
		echo "images already downloaded!"
	fi

	cd annotations
	pwd

	echo "now downloading fixed ModaNet annotations (this can also be done with datasets fix command)"
	wget -N https://github.com/cad0p/maskrcnn-modanet/releases/download/v0.9/instances_all.json
	
	cd ..
	
else
	echo "images will be downloaded afterwards by running datasets arrange command"
	mkdir images
fi


cd ..
cd .. #now in main folder
mkdir results
cd results
pwd

echo "downloading the default coco snapshot"
wget -N https://github.com/fizyr/keras-maskrcnn/releases/download/0.2.2/resnet50_coco_v0.2.0.h5


echo "downloading the last available trained modanet snapshot"
wget -N https://github.com/cad0p/maskrcnn-modanet/releases/download/v1.0/resnet50_modanet.h5

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


