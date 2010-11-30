#!/bin/bash

if [[ $# -lt 3 ]]
then
	echo "Modo de usar: $0 Dispositivo NumeroDoTitulo DiretorioDeDestino"
	exit 1
fi

# In a new version i'll make a better option parsing.

TITLE=${2:=1}
DEST=$3
DVDDEVICE=${1:="/dev/cdrom"}

getDvdMetadata()
{
	CHAPTERS=$(mplayer -identify -frames 0 dvd://$TITLE/$DVDDEVICE 2>/dev/null | grep ID_DVD_TITLE_${TITLE}_CHAPTERS | awk -F"=" '{ print $2 }')
	NAME="$(mplayer -identify -frames 0 dvd://$TITLE/$DVDDEVICE 2>/dev/null | grep ID_DVD_VOLUME_ID | awk -F"=" '{ print $2 }')"

}

conversionProcess()
{
	echo -e '\E[1;31m'"\033[1m=> Conversao Iniciada\033[0m"
	rm -f /tmp/encodingtmp.wav
	mkfifo /tmp/encodingtmp.wav

	for CHAPTER in $(seq 1 $CHAPTERS)
	do
		echo -e '\E[1;31m'"\033[1m==> Conversao em progresso... $CHAPTER de $CHAPTERS\033[0m"
		nohup mplayer dvd://$TITLE/$DVDDEVICE -chapter $CHAPTER-$CHAPTER -vc dummy -vo null -ao pcm:file=/tmp/encodingtmp.wav 2>/dev/null >/dev/null &
		lame --quiet --preset insane /tmp/encodingtmp.wav $DEST/$NAME\_$CHAPTER.mp3
	done
	rm -f /tmp/encodingtmp.wav
	echo -e '\E[1;31m'"\033[1m=> Conversao Terminada\033[0m"
}

getDvdMetadata
conversionProcess
