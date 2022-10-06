import os, sys, logging
from logging.handlers import RotatingFileHandler

import numpy as np
import panoramasdk

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

    MODEL_ASSET_NAME = '{{ cookiecutter.model_asset_name }}'
    MODEL_INPUT_NAME = '{{ cookiecutter.model_input_name }}'
    MODEL_INPUT_SIZE = ({{ cookiecutter.model_processing_height }}, {{ cookiecutter.model_processing_width }})

    def __init__(self):
        super().__init__()
        global logger
        self.logger = logger
        self.model = lambda img: self.call({ self.MODEL_INPUT_NAME: img }, self.MODEL_ASSET_NAME)
        self.frame_idx = 0

    def process_frame(self, frame):
        # TODO: resize input to MODEL_INPUT_SIZE
        fake_frame = np.rand(1, 3, *self.MODEL_INPUT_SIZE)
        output = self.model(fake_frame)
        return output

    def process_streams(self):
        streams = self.inputs.video_in.get()
        for stream in streams:
            output = self.process_frame(stream.image)
            print('Model output:', output)
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
