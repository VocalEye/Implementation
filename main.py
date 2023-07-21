import argparse
from keras.models import load_model
from src.real.processor import processRealInput
from src.synthetic.processor import processSyntheticInput

MODEL = load_model('./resources/models/inception.h5')
INPUT = './resources/video/A.mp4'

parser = argparse.ArgumentParser(description='VocalEye ocular communication system')

parser.add_argument('-o', '--operationMode',
                    type=str,
                    choices=['camera', 'synthetic'],
                    default='camera', required=True,
                    help='Operation mode')
parser.add_argument('-v', '--videoDev', type=int, required=False, default=0, help='Video device id')

args = parser.parse_args()

if args.operationMode == 'camera':
    processRealInput(args.videoDev, MODEL)
elif args.operationMode == 'synthetic':
    processSyntheticInput(INPUT, MODEL)
