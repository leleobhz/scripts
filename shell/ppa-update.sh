#!/bin/bash

SOURCES_D_FOLDER="/etc/apt/sources.list.d"

# Hammer
LAST_U_VER=$(curl -s -o- http://archive.ubuntu.com/ubuntu/dists/ | awk -v RS='<[/]?a[^>]*>' '!/td/ && !/archive/ && !/body/ && !/th/ && /.*\// && !/.*-./ {x[i++]=$0} END{print substr (x[i-1], 0, length(x[i-1])-1)}')

function update_src_file
{
	OLD_VER=`basename $1 .list | awk -v FS="-" '{print $NF}'`
	sudo perl -p -i -e 's/'$OLD_VER'/'$LAST_U_VER'/g' $1 
	sudo mv $1 `echo $1 | sed -e 's/'$OLD_VER'/'$LAST_U_VER'/g'`
}

# Do a tar backup

echo "Doing a backup"
sudo tar cPf ${SOURCES_D_FOLDER}.tar ${SOURCES_D_FOLDER}
echo "Done"
echo

for i in $SOURCES_D_FOLDER/*;
do
	VALID_REPO=0
	for LINK in `cat $i | grep -v '^#' | grep -oP "\b(([\w-]+://?|www[.])[^\s()<>]+(?:\([\w\d]+\)|([^[:punct:]\s]|/)))"`
	do
		if [[ $LINK ]];
		then
			echo "Checking for existence of $LINK"
			wget -q --spider -O/dev/null $LINK/dists/$LAST_U_VER/Release
			if [[ $? != 0 ]];
			then
				# If some line is wrong, reject file
				VALID_REPO=1
				break
			fi
		fi
	done

	if [[ $VALID_REPO == 0 ]];
	then
		echo "Valid link for $LINK in version $LAST_U_VER. Proceeding..."
		update_src_file $i
	else
		echo "Not valid link for $LINK in version $LAST_U_VER. Aborting the repository..."
	fi
echo
done
