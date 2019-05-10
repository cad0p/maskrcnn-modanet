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
	wget http://vision.is.tohoku.ac.jp/chictopia2/photos.lmdb.tar
	tar xf photos.lmdb.tar
	rm photos.lmdb.tar
else echo "photos database already downloaded!"
fi
gunzip -c chictopia.sql.gz | sqlite3 chictopia.sqlite3
rm chictopia.sql.gz

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
mkdir logs

tree -d $PATH1 -I lib --matchdirs


