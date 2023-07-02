#!/bin/sh

# Ouvrir le service SocketIO (chat et vidéo) dans un terminal
osascript -e 'tell application "Terminal" to do script "cd /Users/LKorenfeld/Documents/Travail/ITS/projetinterop/messagerie/www/mon-chat-video && npm run start"'

# Ouvrir le service web dans un terminal
osascript -e 'tell application "Terminal" to do script "python /Users/LKorenfeld/Documents/Travail/ITS/projetinterop/run.py"'

# Ouvrir le service HL7 FHIR dans un terminal
osascript -e 'tell application "Terminal" to do script "python /Users/LKorenfeld/Documents/Travail/ITS/projetinterop/fhir_service.py"'
