#!/bin/bash

if [ -z $1 ]; then
	target="world"
else
	target=$1
fi

echo "Hello, $target"
