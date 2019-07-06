A Mask R-CNN Keras implementation with Modanet annotations on the Paperdoll dataset

# Mask R-CNN with ModaNet

My bachelor's thesis project.

![ModaNet](https://github.com/eBay/modanet/blob/master/logo/modanet_logo2.png)

To sum it all up, I created a program that enables you to quickly train any model using [fizyr's keras-maskrcnn](https://github.com/fizyr/keras-maskrcnn) (I spent around a month to make it work).
And in particular to train it using [ModaNet](https://github.com/eBay/modanet).
ModaNet, I discovered, had its flaws, particularly on the footwear and boots. They had the bounding boxes overlap with each other.
You can check them out by running `maskrcnn-modanet viewimage --all-set --original`
With and without the "original" parameter, in parallel in two different terminal tabs/windows.

So I fixed them (although help is much appreciated to refine it).

Then I ran some tests to check the results and footwear and boots recognition were dramatically improved.

I then formulated a simple application to analyze how many shoes, or skirts, or one of the other 13 labels, are in the user's instagram account, only analyzing images in which there is only one person in the frame. More details again on the [release notes for v1.0](https://github.com/cad0p/maskrcnn-modanet/releases/tag/v1.0).

Below is the home screen of the program.

```
Usage: maskrcnn-modanet [OPTIONS] COMMAND [ARGS]...

  Main CLI.

Options:
  --help  Show this message and exit.

Commands:
  datasets        Manage your datasets run 1 -> maskrcnn-modanet datasets...
  evaluate        Evaluate any trained model, average precision and recall.
  instagram       Simple implementation to track instagram metrics per...
  processimage    View and save processed image and annotations from input...
  savedvars       Show and edit saved variables
  train           Train using the dataset downloaded usage: maskrcnn-
                  modanet...
  viewannotation  View and (not yet needed) save dataset images, plain (not...
  viewimage       View and (not yet needed) save dataset images, plain (not...


```
I'll be very happy to merge your pull requests that add new implementations, or link to them in a section here!

## Getting Started

This project is written in Python 3, so it works in all major OSes. Although only Linux and MacOS are fully supported.
Keep in mind to use pip or pip3 depending on your settings.

Clone this repo

Run `pip install maskrcnn-modanet --user`

Or go to the repo you just cloned on the terminal and run `pip install . -e --user`

Now that you've installed it, run `maskrcnn-modanet datasets download the/folder/you/want/to/put/data/in`

It will take a while, about 40GB to download!
EDIT: it is now reduced to just 2-3 GB. See the [release notes for v1.0](https://github.com/cad0p/maskrcnn-modanet/releases/tag/v1.0) for details on this and on the instagram application. 

Then you can explore its features and commands by running `maskrcnn-modanet`

### Prerequisites

Install Python and Keras

Install [Git LFS (Large File Storage)](https://github.com/git-lfs/git-lfs/wiki/Installation) to get all the files!

<!--## Files used

* teslasheet [on my Drive](https://docs.google.com/spreadsheets/d/1wCQQs4Db_8AbxcvRWW3v0yB4pYNEC7v6ckFMnnmIEE4/edit?usp=sharing) - created with [SourceFiles](SourceFiles) taken from [Tesla Motors Club Forum](https://teslamotorsclub.com/tmc/threads/breaking-down-the-model-s-range-calculator-hidden-features-and-data.94675/#post-2692441)-->

## Built With

* [Sublime Text](https://www.sublimetext.com/) - The text editor used
* [Python 3](https://www.python.org) - Language utilized
* [GitHub Desktop](https://desktop.github.com/) - To manage developement
* [Sublime Merge](https://www.sublimemerge.com/) - To manage developement

## Contributing

The following is a copy of PurpleBooth
> Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

For the versions available, see the [releases on this repository](../../releases). 

## Authors

* **Pier Carlo Cadoppi** - *Initial work*

See also the list of [contributors](../../contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
*  * **Billie Thompson** - *README Template* - [PurpleBooth](https://github.com/PurpleBooth)
* Inspiration
* etc lol
