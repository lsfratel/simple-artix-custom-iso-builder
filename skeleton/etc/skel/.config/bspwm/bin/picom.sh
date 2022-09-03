#!/usr/bin/env bash

CONFIG=(~/.config/bspwm/picom/picom.conf)

if [[ `pidof picom` ]]; then
    pkill picom
	while pgrep -u $UID -x picom >/dev/null; do
        sleep 1;
    done
fi

picom \
    --config "${CONFIG[@]}" &
