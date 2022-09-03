#!/usr/bin/env bash

ps=(picom dunst nm-applet volumeicon mictray sxhkd)
for p in "${ps[@]}"; do
	if [[ `pidof ${p}` ]]; then
		killall -9 ${p}
	fi
done

if [[ ! `pidof lxpolkit` ]]; then
	/usr/bin/lxpolkit &
fi

# Fix cursor
xsetroot -cursor_name left_ptr

# Load apps rules
~/.config/bspwm/rules.sh &

# Set shortcuts
sxhkd -c ~/.config/bspwm/sxhkdrc &

# NetworkManager tray
nm-applet &

# Mic tray
mictray &

# Clipboard tray
parcellite &

# Volume tray
volumeicon &

# Restore wallpaper
nitrogen --restore &

# Lauch notification daemon
~/.config/bspwm/bin/dunst.sh &

# Lauch compositor
~/.config/bspwm/bin/picom.sh &

# Lauch polybar
~/.config/bspwm/bin/polybar.sh &
