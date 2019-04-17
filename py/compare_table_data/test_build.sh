#!/usr/bin/env bash

VERSION=0.2

rm -r ./dist/
pyinstaller ./compare.py
cp ./dbs.properties ./dist/compare/
zip -r ./dist/"compare-$VERSION".zip ./dist/compare/
