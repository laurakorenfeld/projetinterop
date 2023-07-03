import curses
import urllib

# from fhirclient.models.serveur_fhirointment import Appointment
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from serveur_fhir import serveur_fhir
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
#from serveur_fhir import utils
import json, os
from flask_login import LoginManager, login_user, UserMixin, logout_user, login_required
from flask import flash
from flask_login import current_user
from dateutil.parser import parse
from hl7apy.core import Message
import bcrypt
from serveur_fhir import utils
@serveur_fhir.route('/metadata', methods=['GET'])
def metadata():
    # get the resources supported
    resources = ["Patient", "Consultation"]

    # get the interactions and operations supported for each resource
    interactions = {
        "Patient": ["Create", "Read", "Update"],
        "Consultation": ["Create", "Read"]
    }

    # get the search parameters supported for each resource
    search_params = {
        "Patient": ["id", "name", "birthdate"],
        "Consultation": ["id", "patient_id", "date"]
    }

    # get the security requirements
    security = "SSL/TLS"

    # create a dictionary with the metadata
    metadata = {
        "resources": resources,
        "interactions": interactions,
        "search_params": search_params,
        "security": security
    }

    # return the metadata as a JSON object
    return jsonify(metadata)

@serveur_fhir.route("/")
def acc():
    return redirect('http://0.0.0.0:8080')
@serveur_fhir.route("/fhir/Patient")
def patient_list():
    patients = utils.load_patient()
    return render_template('patient.html', patients=patients)
    # return patients


@serveur_fhir.route("/fhir/Patient/<int:patient_id>")
def patient_details(patient_id):
    patient = utils.get_patient_by_id(patient_id)
    #return redirect(urllib.request.urlopen('http://0.0.0.0:8000'))
    return render_template('patient_detail.html', patient=patient)


@serveur_fhir.route('/fhir', methods=['GET','POST'])
def fhir():
    return render_template('acc_medecin.html')


@serveur_fhir.route('/fhir/page_ajout_patient', methods=['GET', 'POST'])
def page_ajout_patient():
    # id = compte fichier +1 (un truc du genre)
    if request.method == 'GET':
        return render_template('ajout_patient.html')
    else:
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        genre = request.form["genre"]
        # Récupération de la date depuis le formulaire
        date_naiss = request.form["date_naissance"]
        # Conversion de la date en un objet datetime
        date = datetime.strptime(date_naiss, '%Y-%m-%d')
        # Formatage de la date dans le format JJ/MM/AAAA
        date_str = date.strftime('%d/%m/%Y')
        #patients = utils.read_json(os.path.join(serveur_fhir.root_path, 'data/Patients/Patient' + str(id) + '.json'))
        # Chemin vers le répertoire où sont stockées les données des patients
        directory = os.path.join(serveur_fhir.root_path, 'data/Patients/')

        # Obtenir une liste de tous les fichiers dans le répertoire
        files = os.listdir(directory)

        # Filtrer la liste pour inclure uniquement les fichiers .json
        json_files = [file for file in files if file.endswith('.json')]

        # Le nouvel ID sera le nombre actuel de fichiers json plus 1
        new_id = len(json_files) + 1

        new_patient = {
            "resourceType": "Patient",
            "identifier": [
                {
                    "use": "official",
                    "system": "http://example.com/identifier",
                    "value": str(new_id)
                }
            ],
            "active": True,
            "name": [
                {
                    "family": nom,
                    "given": [prenom],
                }
            ],
            "telecom": [
                {
                    "system": "phone",
                    "value": "555-555-5555"
                },
                {
                    "system": "email",
                    "value": "test@example.com"
                }
            ],
            "gender": genre,
            "birthDate": date_str,
        }

        with open(os.path.join(directory, 'Patient' + str(new_id) + '.json'), 'w') as f:
            json.dump(new_patient, f)
        return redirect(url_for('patient_list'))

@serveur_fhir.route('/fhir/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = utils.get_patient_by_id2(patient_id)
    if request.method == 'GET':
        return redirect(url_for('patient_detail', patient_id=patient_id))
    elif request.method == 'POST':
        # Code pour mettre à jour les informations du patient
        return redirect(url_for('patient_detail', patient_id=patient_id))

@serveur_fhir.route('/fhir/patient_detail/<int:patient_id>/delete', methods=['POST'])
def delete_patient(patient_id):
    utils.delete_patient(patient_id)
    flash("Le patient a été supprimé avec succès.")
    return redirect(url_for('patient_list'))



@serveur_fhir.route('/fhir/rech_patient', methods=['GET', 'POST'])
def rech_patients():
    #return(redirect("http://0.0.0.0:8000/fhir/rech_patient"))
    if request.method == 'GET':
        return render_template('affiche_patient.html')
    else:
        patient_id = request.form['patient_id']
        if patient_id:
            # Redirige l'utilisateur vers la page 'patient_detail.html' avec l'identifiant du patient en paramètre
            return redirect('/fhir/patient_detail/' + str(patient_id))
        else:
            return 'Patient non trouvé'


@serveur_fhir.route('/fhir/patient_detail/<int:patient_id>')
def patient_detail(patient_id):
    print(patient_id)
    # patients = utils.load_patient()
    patient = utils.get_patient_by_id2(patient_id)
    print(patient)
    if patient:
        return render_template('patient_detail.html', patient=patient)
    else:
        return 'Patient non trouvé'


@serveur_fhir.route('/patients/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def personne(id):
    conn = sqlite3.connect('dossiers_medicaux.db')
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM patient WHERE id={}".format(id))
        rows = cursor.fetchall()
        for r in rows:
            personne = r
        if personne is not None:
            return jsonify(personne), 200
        else:
            return "Something wrong", 404
    if request.method == 'PUT':
        sql = """UPDATE patient
            SET nom=?,
                prenom=?,
                genre=?,
                materiel=?,
                recherche=?
            WHERE id=?"""
        nom = request.form['nom']
        prenom = request.form['prenom']
        genre = request.form['genre']
        materiel = request.form['materiel']
        recherche = request.form['recherche']
        updated_patient = {
            "id": id,
            "nom": nom,
            "prenom": prenom,
            "genre": genre,
            "materiel": materiel,
            "recherche": recherche
        }
        conn.execute(sql, (nom, prenom, genre, materiel, recherche, id))
        conn.commit()
        return jsonify(updated_patient)

    if request.method == 'DELETE':
        sql = """DELETE FROM patient WHERE id=?"""
        conn.execute(sql, (id,))
        conn.commit()
        return "La personne avec id est {} a été effacée".format(id), 201


@serveur_fhir.route("/patientjson/<id>")
def userdata(id):
    document_path = os.getcwd() + '/serveur_fhir/data/Patients/Patient' + id + '.json'
    f = open(document_path, 'r')
    data = json.load(f)
    f.close()
    return data


def immunizationdata(id):
    document_path = os.getcwd() + '/serveur_fhir/data/immunization/' + id + '.json'
    f = open(document_path, 'r')
    data = json.load(f)
    f.close()
    return data

@serveur_fhir.route("/patient/<id>")
def patient(id):
    patient = userdata(id)
    return render_template('patient_detail.html', patient=patient)


@serveur_fhir.route("/immunization/<id>")
def immunization(id):
    data = immunizationdata(id)
    return render_template('immunization.html', utilisateur=data)


@serveur_fhir.route('/serv/<id>')
def get_patient_from_server(id):
    url = urllib.request.urlopen('http://0.0.0.0:8000/data/Patients/Patient' + id)
    data = json.load(url)
    return render_template('patient_detail.html', patient=data)

@serveur_fhir.route('/<name>')
def nom(name):
    return 'Salut! Je pense que tu as fait une erreur dans ta requête : {}'.format(name)
