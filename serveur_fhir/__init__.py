from flask import Flask

serveur_fhir = Flask(__name__, static_folder='static')

from serveur_fhir import views, utils


