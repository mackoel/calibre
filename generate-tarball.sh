#!/bin/sh

VERSION=$1

tar -xvzf calibre-$VERSION.tar.gz
rm -f calibre/resources/fonts/liberation/*
rm -f calibre/resources/fonts/prs500/*

tar -cvzf calibre-$VERSION-nofonts.tar.gz calibre
