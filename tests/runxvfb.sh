#!/bin/bash
DIST=$1
set -e
xlogo &
XLOGO_PID=$!
xmessage -center "`ls -la /`" &
XMSG_PID=$!

sleep 1

nosetests -v test_scrot.py test_imagemagick.py
nosetests -v test_def.py

if [[ ${DIST} != "general" ]];then
    PYTHON_VERSION=$2
    PY=${PYTHON_VERSION:0:1}
    if [[ ${DIST} != "trusty" ]];then
        nosetests -v test_pygdk3_conflict.py
        nosetests -v test_pygdk3.py
        nosetests -v test_pyqt5.py
    fi
    if [[ ${DIST} != "xenial" ]];then
    if [[ ${PY} == "2" ]];then
        nosetests -v test_wx.py
    fi
    fi
    nosetests -v test_pyqt4.py
    nosetests -v test_pyside.py
    if [[ ${PY} == "2" ]];then
        nosetests -v test_pygtk.py
    fi

    if [[ ${DIST} == "bionic" ]];then
        nosetests -v test_qtpy.py
        nosetests -v test_pyside2.py
    fi
fi
#nosetests -v test_gnome_screenshot.py
#nosetests -v test_mac_quartz.py
#nosetests -v test_mac_screencapture.py

nosetests -v easy

kill $XLOGO_PID
kill $XMSG_PID