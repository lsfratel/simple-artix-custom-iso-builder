#!/usr/bin/env bash

CONFIG=(~/.config/bspwm/polybar/config.ini)

if [[ ! `pidof polybar` ]]; then
	polybar -q main -c "${CONFIG[@]}" &
else
	polybar-msg cmd restart
fi

