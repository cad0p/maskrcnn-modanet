import setuptools

with open("README.MD", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='maskrcnn-modanet',  
    version='0.1',
    #scripts=['maskrcnn-modanet'] ,
    author="Pier Carlo Cadoppi",
    author_email="piercarlo.cadoppi@studenti.unipr.it",
    description="A MaskRCNN Keras implementation with Modanet annotations on the Paperdoll dataset",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cad0p/maskrcnn-modanet",
    packages= ['maskrcnn_modanet'] , #setuptools.find_packages(),
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
      'tensorflow',
      'tensorflow-gpu',
      'instaloader'
    ],
    entry_points = {
        'console_scripts': [
            'maskrcnn-modanet=maskrcnn_modanet.cli.main:main',
        ],
    }

 )