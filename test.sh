#\bin\bash
filesize=`sudo du -s ~/Pictures | awk '{ print $1 }'`
maxsize=$((1024*1024))
if [ $filesize -lt $maxsize ]
then
	HOST='192.168.50.1'
	USER='admin-zjj'
	PASSWD='NET5514zjj@@'
	FILE='~/Pictures/*'
	DEST='Portable_HDD/ZJJ-ADMIN/surv'
	ftp -n $HOST
	user $USER
	quote PASS $PASSWD
	binary
	cd $DEST
	put FILE
	quit
	END_SCRIPT
fi

