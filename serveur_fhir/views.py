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

@serveur_fhir.route("/")
def acc():
    return redirect('https://0.0.0.0:8080')
@serveur_fhir.route('/fhir', methods=['GET','POST'])
def fhir():
    return render_template('acc_medecin.html')

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

@serveur_fhir.route('/fhir/page_ajout_patient', methods=['GET', 'POST'])
def page_ajout_patient():
    if request.method == 'GET':
        return render_template('ajout_patient.html')
    else:
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        genre = request.form["genre"]
        date_naiss = request.form["date_naissance"]
        date = datetime.strptime(date_naiss, '%Y-%m-%d')
        date_str = date.strftime('%Y-%m-%d')

        new_id = utils.get_next_patient_id()  # Obtenez le nouvel identifiant du patient

        new_patient = {
            "resourceType": "Patient",
            "id": str(new_id),
            "text": {
                "status": "generated",
                "div": "<div xmlns=\"http://www.w3.org/1999/xhtml\"><p style=\"border: 1px #661aff solid; background-color: #e6e6ff; padding: 10px;\"><b>" + prenom + "</b> " + genre + ", DoB: " + date_str + " (Medical record number: " + str(new_id) + " (use: USUAL, period: 2001-05-06 --&gt; (ongoing)))</p><hr/><table class=\"grid\"><tr><td style=\"background-color: #f3f5da\" title=\"Record is active\">Active:</td><td>true</td><td style=\"background-color: #f3f5da\" title=\"Known status of Patient\">Deceased:</td><td colspan=\"3\">false</td></tr><tr><td style=\"background-color: #f3f5da\" title=\"Alternate names (see the one above)\">Alt Names:</td><td colspan=\"3\"><ul><li>" + nom + " " + prenom + " (OFFICIAL)</li></ul></td></tr><tr><td style=\"background-color: #f3f5da\" title=\"Ways to contact the Patient\">Contact Details:</td><td colspan=\"3\"><ul><li>-unknown-(HOME)</li><li>ph: 555-555-5555(WORK)</li><li>ph: 555-555-5555(MOBILE)</li><li>ph: 555-555-5555(OLD)</li><li>534 Erewhon St PeasantVille, Rainbow, Vic 3999(HOME)</li></ul></td></tr><tr><td style=\"background-color: #f3f5da\" title=\"Nominated Contact: Next-of-Kin\">Next-of-Kin:</td><td colspan=\"3\"><ul><li>Bénédicte du Marché  (female)</li><li>534 Erewhon St PleasantVille Vic 3999 (HOME)</li><li><a href=\"tel:+33(237)998327\">+33 (237) 998327</a></li><li>Valid Period: 2012 --&gt; (ongoing)</li></ul></td></tr><tr><td style=\"background-color: #f3f5da\" title=\"Patient Links\">Links:</td><td colspan=\"3\"><ul><li>Managing Organization: <a href=\"organization-example-gastro.html\">Organization/1</a> &quot;Gastroenterology&quot;</li></ul></td></tr></table></div>"
            },
            "identifier": [{
                "use": "usual",
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "MR"
                    }]
                },
                "system": "urn:oid:1.2.36.146.595.217.0.1",
                "value": str(new_id),
                "period": {
                    "start": "2001-05-06"
                },
                "assigner": {
                    "display": "Acme Healthcare"
                }
            }],
            "active": True,
            "name": [{
                "use": "official",
                "family": nom,
                "given": [prenom]
            }],
            "telecom": [
                {"use": "home"},
                {
                    "system": "phone",
                    "value": "555-555-5555",
                    "use": "work",
                    "rank": 1
                },
                {
                    "system": "phone",
                    "value": "555-555-5555",
                    "use": "mobile",
                    "rank": 2
                },
                {
                    "system": "phone",
                    "value": "555-555-5555",
                    "use": "old",
                    "period": {
                        "end": "2014"
                    }
                }
            ],
            "gender": genre,
            "birthDate": date_str,
            "_birthDate": {
                "extension": [{
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-birthTime",
                    "valueDateTime": date_str + "T14:35:45-05:00"
                }]
            },
            "deceasedBoolean": False,
            "address": [
                {
                    "use": "home",
                    "type": "both",
                    "text": "534 Erewhon St PeasantVille, Rainbow, Vic 3999",
                    "line": ["534 Erewhon St"],
                    "city": "PleasantVille",
                    "district": "Rainbow",
                    "state": "Vic",
                    "postalCode": "3999",
                    "period": {
                        "start": date_str
                    }
                }
            ],
            "contact": [
                {
                    "relationship": [
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v2-0131",
                                    "code": "N"
                                }
                            ]
                        }
                    ],
                    "name": {
                        "family": "du Marché",
                        "_family": {
                            "extension": [
                                {
                                    "url": "http://hl7.org/fhir/StructureDefinition/humanname-own-prefix",
                                    "valueString": "VV"
                                }
                            ]
                        },
                        "given": ["Bénédicte"]
                    },
                    "telecom": [
                        {
                            "system": "phone",
                            "value": "+33 (237) 998327"
                        }
                    ],
                    "address": {
                        "use": "home",
                        "type": "both",
                        "line": ["534 Erewhon St"],
                        "city": "PleasantVille",
                        "district": "Rainbow",
                        "state": "Vic",
                        "postalCode": "3999",
                        "period": {
                            "start": date_str
                        }
                    },
                    "gender": "female",
                    "period": {
                        "start": "2012"
                    }
                }
            ],
            "managingOrganization": {
                "reference": "Organization/1"
            }
        }

        # Sauvegarder le nouveau patient dans un fichier JSON
        file_path = os.path.join(serveur_fhir.root_path, 'data/Patients/Patient' + str(new_id) + '.json')
        with open(file_path, 'w') as f:
            json.dump(new_patient, f)

        return redirect(url_for('patient_list'))
@serveur_fhir.route('/fhir/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    patient = utils.get_patient_by_id2(patient_id)
    if request.method == 'GET':
        return render_template('edit_patient.html', patient=patient, patient_id=patient_id)
    elif request.method == 'POST':
        # Récupérer les données du formulaire
        updated_patient = {
            'nom': request.form.get('nom'),
            'prenom': request.form.get('prenom'),
            'genre': request.form.get('genre'),
            # ... tout autre champ du formulaire que vous voulez mettre à jour
        }
        utils.update_patient(patient_id, updated_patient)
        return redirect(url_for('patient_detail', patient_id=patient_id))


@serveur_fhir.route('/fhir/patient_detail/<int:patient_id>/delete', methods=['GET','POST','DELETE'])
def remove_patient(patient_id):
    utils.delete_patient(patient_id)
    #flash("Le patient a été supprimé avec succès.")
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
