import argparse
import time
import os
import subprocess
import cv2 as cv
import numpy as np

FLAGS = None
VID = 'video'
IMG = 'image'

meanX = 103.939
meanY = 116.779
meanZ = 123.680

def nothing(v):
    print('hello ' + v)

def predict_all(img, values, h, w):
    blob = cv.dnn.blobFromImage(img, 1.0, (w, h),
        (meanX, meanY, meanZ), swapRB=False, crop=False)

    sum = 0
    for value in values:
        sum += value

    out = cv.normalize(img, None, 0, 255, cv.NORM_MINMAX, cv.CV_8U)
    if sum == 0:
        return out

    weights = []
    for value in values:
        weights.append(value / sum)

    num_models = 0
    for i in range(0, len(nets)):
        if weights[i] != 0:
            net = nets[i]

            print ("[INFO] Applying model " + str(i) + ", weight: " + str(weights[i]))
            if num_models == 0:
                out = predict(blob, net, h, w) * weights[i]
            else:
                out += predict(blob, net, h, w) * weights[i]

            num_models = num_models + 1
    return out

def predict(blob, net, h, w):
    print ('[INFO] Setting the input to the model')
    net.setInput(blob)

    print ('[INFO] Starting Inference!')
    start = time.time()
    out = net.forward()
    end = time.time()
    print ('[INFO] Inference Completed successfully!')

    # Reshape the output tensor and add back in the mean subtraction, and
    # then swap the channel ordering
    out = out.reshape((3, out.shape[2], out.shape[3]))
    out[0] += meanX
    out[1] += meanY
    out[2] += meanZ
    out /= 255.0
    out = out.transpose(1, 2, 0)

    # Printing the inference time
    if FLAGS.print_inference_time:
        print ('[INFO] The model ran in {:.4f} seconds'.format(end-start))

    return out

# Source for this function:
# https://github.com/jrosebr1/imutils/blob/4635e73e75965c6fef09347bead510f81142cf2e/imutils/convenience.py#L65
def resize_img(img, width=None, height=None, inter=cv.INTER_AREA):
    dim = None
    h, w = img.shape[:2]

    if width is None and height is None:
        return img
    elif width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    elif height is None:
        r = width / float(w)
        dim = (width, int(h * r))

    resized = cv.resize(img, dim, interpolation=inter)
    return resized

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model-path',
                type=str,
                default='./models/instance_norm/',
                help='The model directory.')

    parser.add_argument('-i', '--image',
                type=str,
                help='Path to the image.')

    parser.add_argument('-md', '--model',
                type=str,
                help='The file path to the direct model.\
                 If this is specified, the model-path argument is \
                 not considered.')

    parser.add_argument('--show-original-image',
                type=bool,
                default=False,
                help='Whether or not to show the original image')

    parser.add_argument('--save-image-with-name',
                type=str,
                default='stylizedimage.png',
                help='The path to save the generated stylized image \
                       only when in image mode.')

    parser.add_argument('--download-models',
                type=bool,
                default=False,
                help='If set to true all the pretrained models are downloaded, \
                    using the script in the downloads directory.')

    parser.add_argument('--print-inference-time',
                type=bool,
                default=False,
                help='If set to True, then the time taken for the model is output \
                    to the console.')

    FLAGS, unparsed = parser.parse_known_args()

    # download models if needed
    if FLAGS.download_models:
        subprocess.call(['./models/download.sh'])

    # Set the mode image/video based on the argparse
    if FLAGS.image is None:
        mode =  VID
    else:
        mode = IMG

    # Check if there are models to be loaded and list them
    models = []
    for f in sorted(os.listdir(FLAGS.model_path)):
        if f.endswith('.t7'):
            models.append(f)

    if len(models) == 0:
        raise Exception('The model path doesn\'t contain models')

    # Load the neural style transfer model
    path = FLAGS.model_path + ('' if FLAGS.model_path.endswith('/') else '/')
    print (path + models[0])
    print ('[INFO] Loading the model...')

    total_models = len(os.listdir(FLAGS.model_path))

    nets = []
    for model in models:
        model_to_load = path + model
        nets.append(cv.dnn.readNetFromTorch(model_to_load))

    print ('[INFO] Model Loaded successfully!')

    # Loading the image depending on the type
    if mode == VID:
        pass

        cv.namedWindow("Real-time Video")
        cv.moveWindow("Real-time video", 400, 0)

        cv.namedWindow("Preview")
        cv.moveWindow("Preview", 0, 0)

        vid = cv.VideoCapture(0)
        while True:
            _, frame = vid.read()
            img = resize_img(frame, width=400)
            h, w  = img.shape[:2]
            cv.imshow("Real-time Video", img)

            fValues = open("values.txt", "rt")
            lines = fValues.read().splitlines()
            fValues.close()

            values = []
            svalues = lines[0].split(';')
            for i in range(0,6):
                values.append(int(svalues[i]))

            out = predict_all(img, values, h, w)
            cv.imshow('Preview', out)

            if os.path.exists("./shoot"):
                os.system("rm -f shoot")

                frame_normed = 255 * (out - out.min()) / (out.max() - out.min())
                frame_normed = np.array(frame_normed, np.int)
                cv.imwrite("./picture.jpg", frame_normed)

            key = cv.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('n') and FLAGS.model is None:
                model_loaded_i = (model_loaded_i + 1) % total_models
                model_to_load = path + models[model_loaded_i]
                net = cv.dnn.readNetFromTorch(model_to_load)
            elif key == ord('p') and FLAGS.model is None:
                model_loaded_i = (model_loaded_i - 1) % total_models
                model_to_load = path + models[model_loaded_i]
                net = cv.dnn.readNetFromTorch(model_to_load)

        vid.release()
        cv.destroyAllWindows()
    elif mode == IMG:
        print ('[INFO] Reading the image')
        img = cv.imread(FLAGS.image)
        print ('[INFO] Image Loaded successfully!')

        img = resize_img(img, width=600)
        h, w  = img.shape[:2]

        # Get the output from the pretrained model
        out = predict(img, h, w)

        # show the image
        if FLAGS.show_original_image:
            cv.imshow('Input Image', img)
        cv.imshow('Stylized image', out)

        meanX += 50
        meanY += 50
        meanZ += 50
        out2 = predict(img, h, w)
        cv.imshow('Stylized image 2', out2)

        meanX -= 100
        meanY -= 100
        meanZ -= 100
        out3 = predict(img, h, w)
        cv.imshow('Stylized image 3', out3)

        model_to_load = path + models[1]
        net = cv.dnn.readNetFromTorch(model_to_load)
        out4 = predict(img, h, w)
        cv.imshow('Stylized image 4', out4)

        out5 = (out + out4) * 0.5
        cv.imshow('Stylized image 5', out5)


        print ('[INFO] Hit Esc to close!')
        cv.waitKey(0)

        if FLAGS.save_image_with_name is not None:
            cv.imwrite(FLAGS.save_image_with_name, out)
