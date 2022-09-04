#!/usr/bin/env bash

CONFIG="$HOME/.config/bspwm/alacritty/alacritty.yml"

func_floated() {
	alacritty \
		--class 'alacritty-float,alacritty-float' \
		--config-file "$CONFIG"
}

func_fullscreen() {
	alacritty \
	  	--class 'Fullscreen,Fullscreen' \
	  	--config-file "$CONFIG" \
	  	-o window.startup_mode=fullscreen \
	  	window.padding.x=15 window.padding.y=15 \
	  	window.opacity=0.95 font.size=12
}

func_open() {
	alacritty \
		--class 'alacritty-float,alacritty-float' \
		--config-file "$CONFIG" \
		-e "$1"
}

while getopts ":fue:" option; do
    case $option in
        f)
            func_floated
			exit;;
		u)
			func_fullscreen
			exit;;
		e)
			func_open ${OPTARG}
			exit;;
        \?)
            echo "Invalid option"
            exit ;;
    esac
done

alacritty --config-file "$CONFIG"
