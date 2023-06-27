#!/bin/sh

# Ouvrir le premier service dans un terminal
osascript -e 'tell application "Terminal" to do script "cd /Users/LKorenfeld/Documents/Travail/ITS/projetinterop/messagerie/www/mon-chat-video && npm run start"'

# Ouvrir le deuxième service dans un terminal
osascript -e 'tell application "Terminal" to do script "python /Users/LKorenfeld/Documents/Travail/ITS/projetinterop/run.py"'
