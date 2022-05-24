import setuptools

with open("README.MD", "r") as fh:
		long_description = fh.read()


setuptools.setup(
		name='maskrcnn-modanet',  
		version='1.0.3',
		# scripts=[
		# 	'maskrcnn_modanet/download.sh'
		# ],
		author="Pier Carlo Cadoppi",
		author_email="piercarlo.cadoppi@studenti.unipr.it",
		description="A MaskRCNN Keras implementation with Modanet annotations on the Paperdoll dataset",
		long_description=long_description,
		long_description_content_type="text/markdown",
		url="https://github.com/cad0p/maskrcnn-modanet",
		# packages= ['maskrcnn_modanet'] , 
		packages= setuptools.find_packages(),
		classifiers=[
		 "Programming Language :: Python :: 3",
		 "License :: OSI Approved :: MIT License",
		 "Operating System :: OS Independent",
		],
		install_requires=[
			'keras-maskrcnn',
			'click',
			'progressbar',
			'lmdb',
			'pandas',
			'sqlalchemy',
			'Cython',
			'cython',
			'numpy',
			'pycocotools',
			'matplotlib',
			'tensorflow==2.6.4',
			'keras==2.2.5',
			'keras-retinanet==0.5.1',
			'h5py<3.0.0',
			'instaloader'
		],
		entry_points = {
		    'console_scripts': [
		        'maskrcnn-modanet=maskrcnn_modanet.cli.main:main',
		    ],
		},
		include_package_data=True,
		zip_safe=False

 )
