def draw_mask(image, box, mask, label=None, color=None, binarize_threshold=0.5):
    """ Draws a mask in a given box.
    Args
        image              : Three dimensional image to draw on.
        box                : Vector of at least 4 values (x1, y1, x2, y2) representing a box in the image.
        mask               : A 2D float mask which will be reshaped to the size of the box, binarized and drawn over the image.
        color              : Color to draw the mask with. If the box has 5 values, the last value is assumed to be the label and used to construct a default color.
        binarize_threshold : Threshold used for binarizing the mask.
    """
    if label is not None:
        color = label_color(label)
    if color is None:
        color = (0, 255, 0)

    # resize to fit the box
    mask = mask.astype(np.float32)
    mask = cv2.resize(mask, (box[2] - box[0], box[3] - box[1]))

    # binarize the mask
    mask = (mask > binarize_threshold).astype(np.uint8)

    # draw the mask in the image
    mask_image = np.zeros((image.shape[0], image.shape[1]), np.uint8)
    mask_image[box[1]:box[3], box[0]:box[2]] = mask
    mask = mask_image

    # compute a nice border around the mask
    border = mask - cv2.erode(mask, np.ones((5, 5), np.uint8), iterations=1)

    # apply color to the mask and border
    mask = (np.stack([mask] * 3, axis=2) * color).astype(np.uint8)
    border = (np.stack([border] * 3, axis=2) * (255, 255, 255)).astype(np.uint8)

    # for i in mask:
    # 	for j in i:
    # 		b = False
    # 		for k in i:
    # 			for l in k:
    # 				if l != 0:
    # 					b = True
    # 				if b:
    # 					break
    # 			if b:
    # 				break
    # 		if b:
    # 			print (j)

    # draw the mask
    #import ipdb; ipdb.set_trace()
    indices = np.where(mask != color)
    #print(indices)
    #indices = np.where(mask == []) - indices
    image[indices[0], indices[1], :] = 0 * image[indices[0], indices[1], :] 

    # draw the border
    # indices = np.where(border != [0, 0, 0])
    # image[indices[0], indices[1], :] = 0.2 * image[indices[0], indices[1], :] + 0.8 * border[indices[0], indices[1], :]
def main():
    print("hello")

    MYPATH = "/home/user/piercarlo/"

    # import keras
    import keras

    # import keras_retinanet
    from keras_maskrcnn import models
    #from keras_maskrcnn.utils.visualization import draw_mask
    from keras_retinanet.utils.visualization import draw_box, draw_caption, draw_annotations
    from keras_retinanet.utils.image import read_image_bgr, preprocess_image, resize_image
    from keras_retinanet.utils.colors import label_color

    # import miscellaneous modules
    import matplotlib.pyplot as plt
    import cv2
    import os
    import numpy as np
    import time

    # set tf backend to allow memory to grow, instead of claiming everything
    import tensorflow as tf

    def get_session():
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        return tf.Session(config=config)

    # use this environment flag to change which GPU to use
    #os.environ["CUDA_VISIBLE_DEVICES"] = "1"

    # set the modified tf session as backend in keras
    keras.backend.tensorflow_backend.set_session(get_session())

    # adjust this to point to your downloaded model
    model_path = MYPATH + 'resnet50_coco_v0.2.0.h5'

    # load retinanet model
    model = models.load_model(model_path, backbone_name='resnet50')
    #print(model.summary())

    # load label to names mapping for visualization purposes
    labels_to_names = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 9: 'traffic light', 10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat', 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball', 33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'}

    # load image
    image = read_image_bgr(MYPATH + 'keras-maskrcnn/examples/000000008021.jpg')

    # copy to draw on
    draw = image.copy()
    draw = cv2.cvtColor(draw, cv2.COLOR_BGR2RGB)

    # preprocess image for network
    image = preprocess_image(image)
    image, scale = resize_image(image)

    # process image
    start = time.time()
    outputs = model.predict_on_batch(np.expand_dims(image, axis=0))
    print("processing time: ", time.time() - start)

    boxes  = outputs[-4][0]
    scores = outputs[-3][0]
    labels = outputs[-2][0]
    masks  = outputs[-1][0]

    # correct for image scale
    boxes /= scale

    # visualize detections
    for box, score, label, mask in list(zip(boxes, scores, labels, masks)):
    	if score < 0.5:
    		break

    	color = label_color(label)
    	
    	b = box.astype(int)
    	# draw_box(draw, b, color=color)
    	
    	mask = mask[:, :, label]
    	drawclone = np.copy(draw)
    	draw_mask(drawclone, b, mask, color=label_color(label))

    	caption = "{} {:.3f}".format(labels_to_names[label], score)
    	#draw_caption(draw, b, caption)
    	plt.figure(figsize=(15, 15))
    	plt.axis('off')
    	plt.imshow(drawclone)
    	plt.show()