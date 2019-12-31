#!/usr/bin/env python3
import time
import pychromecast
import argparse
from subprocess import Popen, PIPE, STDOUT

def find_and_connect(cc_name: str) -> pychromecast.Chromecast:
    chromecasts = pychromecast.get_chromecasts()
    print('Found {} cast devices'.format(len(chromecasts)))
    for cc in chromecasts:
        if cc.device.friendly_name == cc_name:
            return cc


def main():
    parser = argparse.ArgumentParser(description='ZAP remote control for chromecast')
    parser.add_argument('ccast_name', type=str, nargs='+', help="Name of the Chromecast or Google home you wnat to control the volume of")
    args = parser.parse_args()

    ccast_name=args.ccast_name
    print('Discovering cast devices...', end = ' ')
    cast=find_and_connect(ccast_name)
    if not cast:
        print('Could not find a cast device named {}'.format(ccast_name))
        exit(1)

    print('Connecting to {}...'.format(ccast_name), end = ' ')
    cast.wait()
    print('Success!')
    current_volume=cast.status.volume_level
    print('Volume: {}'.format(current_volume))

    p = Popen(['/opt/openhab/custom/433Utils/RPi_utils/RFSniffer'], stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    for line in p.stdout:
        code = int(line.decode('utf-8').split(' ')[2].rstrip())
        if code == 5330691: #3 on (left) decrease
            current_volume=cast.status.volume_level
            cast.set_volume(max(current_volume - 0.033, 0))
            print('Volume: {}'.format(current_volume))
        elif code == 5330700: #3 off (right) increase
            current_volume=cast.status.volume_level
            cast.set_volume(min(current_volume + 0.02,1))
            print('Volume: {}'.format(current_volume))

if __name__ == "__main__":
    main()

