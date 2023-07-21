import os
from keras.models import load_model
from src.real.processor import processRealInput

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

MODEL = load_model('./resources/models/inception.h5')

if __name__ == '__main__':
    processRealInput(42, MODEL)