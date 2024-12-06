
NT-Detection-Test - v3 2024-10-30 1:41pm
==============================

This dataset was exported via roboflow.com on October 30, 2024 at 1:44 PM GMT

Roboflow is an end-to-end computer vision platform that helps you
* collaborate with your team on computer vision projects
* collect & organize images
* understand and search unstructured image data
* annotate, and create datasets
* export, train, and deploy computer vision models
* use active learning to improve your dataset over time

For state of the art Computer Vision training notebooks you can use with this dataset,
visit https://github.com/roboflow/notebooks

To find over 100k other datasets and pre-trained models, visit https://universe.roboflow.com

The dataset includes 3549 images.
NT-Detection are annotated in YOLOv8 format.

The following pre-processing was applied to each image:
* Auto-orientation of pixel data (with EXIF-orientation stripping)
* Resize to 800x800 (Stretch)

The following augmentation was applied to create 3 versions of each source image:
* 50% probability of horizontal flip
* 50% probability of vertical flip
* Randomly crop between 0 and 14 percent of the image
* Random rotation of between -27 and +27 degrees
* Random shear of between -18° to +18° horizontally and -18° to +18° vertically
* Random Gaussian blur of between 0 and 1.3 pixels

The following transformations were applied to the bounding boxes of each image:
* Random shear of between -10° to +10° horizontally and -10° to +10° vertically


