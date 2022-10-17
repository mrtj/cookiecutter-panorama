import os, sys, logging
from logging.handlers import RotatingFileHandler

import cv2

import numpy as np
import panoramasdk # type: ignore

TEST_UTILITY_ENVIRONMENT = ('TEST_UTILITY_ENVIRONMENT' in os.environ)

def get_logger(name=__name__, level=logging.INFO, test_utility=False):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    if not test_utility:
        handler = RotatingFileHandler(
            "/opt/aws/panorama/logs/app.log",
            maxBytes=10000000,
            backupCount=2
        )
    else:
        handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

logger = get_logger(level=logging.INFO, test_utility=TEST_UTILITY_ENVIRONMENT)

class Application(panoramasdk.node):

    MODEL_ASSET_NAME: str = '{{ cookiecutter.model_asset_name }}'
    MODEL_INPUT_NAME: str = '{{ cookiecutter.model_input_name }}'
    MODEL_INPUT_WIDTH: int = int('{{ cookiecutter.model_processing_width }}')
    MODEL_INPUT_HEIGHT: int = int('{{ cookiecutter.model_processing_height }}')
    MODEL_INPUT_SIZE = (MODEL_INPUT_WIDTH, MODEL_INPUT_HEIGHT)
    MODEL_INPUT_MEAN = np.array([0.485, 0.456, 0.406])
    MODEL_INPUT_STD = np.array([0.229, 0.224, 0.225])

    def __init__(self):
        super().__init__()
        global logger
        self.logger = logger
        self.model = lambda img: self.call({ self.MODEL_INPUT_NAME: img }, self.MODEL_ASSET_NAME)
        self.frame_idx = 0

    def preprocess(self, frame):
        img = cv2.resize(frame, self.MODEL_INPUT_SIZE, interpolation=cv2.INTER_LINEAR)
        img = img.astype(np.float32) / 255.
        img = (img - self.MODEL_INPUT_MEAN) / self.MODEL_INPUT_STD
        img = np.expand_dims(img.transpose(2, 0, 1), axis=0) # (H, W, C) -> (B, C, H, W)
        return img

    def postprocess(self, output):
        result = output[0] # a tuple is returned, first element is the inference result
        result = np.squeeze(result, axis=0) # we have just one batch here, take it
        result = result.tolist()
        return result

    def process_frame(self, frame):
        img = self.preprocess(frame)
        output = self.model(img)
        result = self.postprocess(output)
        return result

    def process_streams(self):
        streams = self.inputs.video_in.get()
        for stream in streams:
            result = self.process_frame(stream.image)
            msg = 'mean: {}'.format(', '.join('{0:.3f}'.format(c) for c in result))
            stream.add_label(msg, 0.01, 0.1)
        self.outputs.video_out.put(streams)
        if TEST_UTILITY_ENVIRONMENT and self.frame_idx % 10 == 0:
            self.logger.info('processing frame: %s', self.frame_idx)
        self.frame_idx += 1

def main():

    try:
        logger.info('INITIALIZING APPLICATION')
        app = Application()
        logger.info('PROCESSING STREAMS')
        # video processing loop:
        while True:
            app.process_streams()
    except:
        logger.exception('Exception during processing loop.')

main()
