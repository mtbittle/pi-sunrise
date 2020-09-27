#!/bin/phython3
import cec


def is_tv_on():
    cec.init()
    tv = cec.Device(cec.CECDEVICE_TV)
    return tv.is_on()


is_tv_on()
