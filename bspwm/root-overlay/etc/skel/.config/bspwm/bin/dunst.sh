#!/usr/bin/env bash

if [[ `pidof dunst` ]]; then
	pkill dunst
fi

dunst \
	-conf ~/.config/bspwm/dunst/dunstrc &
