#!/bin/bash

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

if [ ! -d "./photos.lmdb"]
then
	wget http://vision.is.tohoku.ac.jp/chictopia2/photos.lmdb.tar
	tar xf photos.lmdb.tar
	rm photos.lmdb.tar
fi
gunzip -c chictopia.sql.gz | sqlite3 chictopia.sqlite3
rm chictopia.sql.gz

cd ..
cd ..
cd ..
pwd
text="now downloading modanet annotations\n
					\t\t\ttaken from here:\n
					\t\t\thttps://github.com/eBay/modanet"

echo $text

# download images annotations
git clone https://github.com/eBay/modanet.git
