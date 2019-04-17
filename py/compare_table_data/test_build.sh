#!/usr/bin/env bash

pyinstaller ./compare.py
cp ./dbs.properties ./dist/compare/
