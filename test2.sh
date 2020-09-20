#!/bin/sh
HOST='192.168.50.1'
USER='admin-zjj'
PASSWD='NET5514zjj@@'
FILE='~/Pictures/*'
DEST='Portable_HDD/ZJJ-ADMIN/test'

ftp -n $HOST <<END_SCRIPT
quote USER $USER
quote PASS $PASSWD
binary
cd $DEST
put $FILE
quit
END_SCRIPT
exit 0
