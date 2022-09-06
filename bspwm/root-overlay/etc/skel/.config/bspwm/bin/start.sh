#!/usr/bin/env bash

ps=(picom dunst sxhkd)
for p in "${ps[@]}"; do
	if [[ `pidof ${p}` ]]; then
		killall -9 ${p}
	fi
done

# Fix cursor
xsetroot -cursor_name left_ptr

# Load apps rules
~/.config/bspwm/rules.sh &

# Set shortcuts
sxhkd -c ~/.config/bspwm/sxhkdrc &

# Lauch notification daemon
~/.config/bspwm/bin/dunst.sh &

# Lauch compositor
~/.config/bspwm/bin/picom.sh &

# Lauch polybar
~/.config/bspwm/bin/polybar.sh &
