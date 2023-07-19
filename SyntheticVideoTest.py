import os
from keras.models import load_model
from src.synthetic.processor import processSyntheticInput

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

SENSIBILITY = 10
MODEL = load_model('./resources/models/inception.h5')
INPUT = './resources/video/A.mp4'

if __name__ == '__main__':
    processSyntheticInput(INPUT, MODEL)