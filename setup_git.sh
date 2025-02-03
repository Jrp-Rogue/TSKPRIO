#!/bin/bash

# Initialiser Git si ce n'est pas déjà fait
if [ ! -d ".git" ]; then
    git init
    git remote add origin https://github.com/Jrp-Rogue/TSKPRIO.git
fi

# Configurer Git (remplace avec ton email et ton nom GitHub)
git config --global user.email "rhogini@gmail.com"
git config --global user.name "Jrp-Rogue"
