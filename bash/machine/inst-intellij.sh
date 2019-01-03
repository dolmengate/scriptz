#! /bin/bash

curl -o page https://www.jetbrains.com/idea/download/#section=linux

if [ $(file -b page | awk '{ print $1 }') = "gzip" ]; then
	mv ./page ./page.gz
	gunzip ./page.gz
fi

VERSION=$(cat page | egrep -o -m 1 '[0-9]{1}\.[0-9]{1}\.[0-9]{1}' | cut -d '.' -f 1-2)
URL=$(printf https://download-cf.jetbrains.com/idea/ideaIC-2018.%b-no-jdk.tar.gz "$VERSION")
rm page
curl -o intellij.tar.gz "$URL"
tar -C /usr/local/bin -x -f intellij.tar.gz
rm intellij.tar.gz
INSTALLDIR=$(find /usr/local/bin -maxdepth 1 -type d -name idea*)
echo "IntelliJ installed to $INSTALLDIR"
