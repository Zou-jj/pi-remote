#\bin\bash
filesize=`sudo du -s ~/Pictures | awk '{ print $1 }'`
maxsize=$((1024*1024))
if [ $filesize -gt $maxsize ]
then
	HOST='192.168.50.1'
	USER='admin-zjj'
	PASSWD='NET5514zjj@@'
	FILE='~/Pictures/*'
	DEST=''
	ftp -n $HOST <<END_SCRIPT
	cd $DEST
	put FILE
	quit
	END_SCRIPT
fi
