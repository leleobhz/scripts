#!/bin/bash

if [[ `uname -m` -eq "x86_64" ]];
then
	BIT="-64bit";
else
	BIT="";
fi

SLSKPATH="/usr/local/bin/"
LAST=`wget -q --user-agent="Wget/leleobhz.org automatic update script v0.1 - Version retrieve step" "http://www.soulseekqt.net/news/node/1" -O- | grep "/SoulseekQT/Linux/" | head -n1 | awk '{ print $3 }' | sed -e "s/\./-/g"`

LINK="http://www.soulseekqt.net/SoulseekQT/Linux/SoulseekQt-$LAST$BIT.tgz"

echo "Updating Soulseek to version $LAST to $SLSKPATH. Please accept sudo credential now."
gksudo true

# Showtime!
TMP=`mktemp`

sudo rm -f $SLSKPATH/soulseek
$(wget -o $TMP --progress=bar:force --user-agent="Wget/leleobhz.org automatic update script v0.1 - File download/pipeline step" $LINK -O- | tar -xzO | sudo dd of=$SLSKPATH/soulseek ; rm -f $TMP) 2>&1>/dev/null &
tail --follow=name $TMP 2>/dev/null | zenity --title="SoulseekQT update progress" --progress --auto-close --auto-kill --no-cancel
sudo chown root.root $SLSKPATH/soulseek
sudo chmod 0755 $SLSKPATH/soulseek

echo "Done!"
