import os
import csv
from pathlib import Path
import pandas as pd
import time
import cv2
import getopt
import sys
import json

if os.path.exists('./dataset') == False:
    raise Exception('Download Dataset')


class Runner:
    def __init__(self, mode, debug):
        self.debug = debug
        self.mode = mode

    def _output(self, row, coords, ms):
        out = {
            'videoId': row['videoId'],
            'frameId': row['frameId'],
        }

        if (len(coords) != len(row['players'])):
            print(
                'partial submission cords length does not equal players length')

        out['time (ms)'] = ms

        out['cords'] = coords

        return out

    def _implementation(self, frame, rink, players):
        return []

    def _images(self):
        with open("submissions/submission.{}.csv".format(int(time.time())), 'w', newline='') as csvfile:
            fieldnames = ['videoId', 'frameId', 'cords', 'time (ms)']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            rows = pd.read_csv('./dataset/players_coords.csv')
            baseRink = cv2.imread('./dataset/rink.jpg')

            for _, row in rows.iterrows():
                img = cv2.imread(row['image'])
                rink = baseRink.copy()

                players = json.loads(row['players'])

                ms = int(round(time.time() * 1000))

                coords = self._implementation(img, rink, players)

                ms = int(round(time.time() * 1000)) - ms

                writer.writerow(self._output(row, coords, ms))

    def _videos(self):
        rows = pd.read_csv('./players_coords.csv')
        baseRink = cv2.imread('./dataset/rink.jpg')

        index = {}

        for _, row in rows.iterrows():
            if row['videoId'] not in index:
                index[row['videoId']] = {
                    "path": row['video'],
                    "frames": {}
                }

            frames = index[row['videoId']]['frames']

            frames[row['frameId']] = row['players']

        for key in index:
            video = index[key]
            cap = cv2.VideoCapture(video['path'])

            while(cap.isOpened()):
                ret, frame = cap.read()

                if ret == True:
                    pos_frame = cap.get(1)

                    players = None

                    if pos_frame in video['frames']:
                        players = video['frames'][pos_frame]

                    if players:
                        rink = baseRink.copy()

                        ms = int(round(time.time() * 1000))

                        coords = self._implementation(frame, rink, players)

                        ms = int(round(time.time() * 1000)) - ms

                    cv2.imshow('scene', frame)

                    cv2.waitKey(10)
                else:
                    break

            cap.release()
            cv2.destroyAllWindows()

    def run(self):
        if self.mode == "video":
            self._videos()
        else:
            self._images()


full_cmd_arguments = sys.argv
argument_list = full_cmd_arguments[1:]
long_options = ["debug", "videos"]

try:
    arguments, values = getopt.getopt(
        argument_list, "", long_options)
except getopt.error as err:
    # Output error, and return with an error code
    print(str(err))
    sys.exit(2)

debug = False
mode = "images"

for current_argument, current_value in arguments:
    if current_argument in ("--videos"):
        mode = "video"
    elif current_argument in ("--debug"):
        debug = True

runner = Runner(mode, debug)
runner.run()
