import curses
import urllib

import cv2
from requests import Response

from app import app
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from app import utils
import json, os
from hl7apy.core import Message

@app.route("/")
def accueil():
    return render_template('index.html')

@app.route("/fhir/acc_medecin")
def acc_medecin():
    return render_template('acc_medecin.html')

@app.route('/metadata', methods=['GET'])
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
    return jsonify(metadata)\

@app.route("/fhir/Patient")
def patient_list():
    patients = utils.load_patient()
    return render_template('patient.html', patients=patients)
    #return patients
@app.route("/fhir/Patient/<int:patient_id>")
def patient_details(patient_id):
    patient = utils.get_patient_by_id(patient_id)
    return render_template('patient_detail.html',patient=patient)

@app.route('/fhir',methods=['GET'])
def aff_acc_med():
    return render_template('acc_medecin.html')

@app.route('/fhir/page_ajout_patient',methods=['GET','POST'])
def page_ajout_patient():
    # id = compte fichier +1 (un truc du genre)
    if request.method == 'GET':
        return render_template('ajout_patient.html')
    else :
        nom = request.form["nom"]
        prenom = request.form["prenom"]
        genre = request.form["genre"]
        # Récupération de la date depuis le formulaire
        date_naiss = request.form["date_naissance"]

        # Conversion de la date en un objet datetime
        date = datetime.strptime(date_naiss, '%Y-%m-%d')

        # Formatage de la date dans le format JJ/MM/AAAA
        id=2
        date_str = date.strftime('%d/%m/%Y')
        patients = utils.read_json(os.path.join(app.root_path, 'data/Patients/Patient'+ str(id) + '.json'))

        new_patient = {
            "resourceType": "Patient",
            "identifier": id + 1,
            "active": True,
            "name": f"{prenom} {nom}",
            "telecom": "...",
            "gender": genre,
            "birthDate": date_str,
        }

        patients.append(new_patient)

        with open(os.path.join(app.root_path, 'data/Patients/patient'+ id + '.json'), 'w') as f:
            json.dump(patients, f)

        return redirect(url_for('patient_list'))


@app.route('/fhir/rech_patient', methods=['GET','POST'])
def rech_patients():
    if request.method == 'GET':
        return render_template('affiche_patient.html')
    else:
        patient_id = request.form['patient_id']
        if patient_id:
            # Redirige l'utilisateur vers la page 'patient_detail.html' avec l'identifiant du patient en paramètre
            return redirect('/fhir/patient_detail/' + str(patient_id))
        else:
            return 'Patient non trouvé'

@app.route('/fhir/patient_detail/<int:patient_id>')
def patient_detail(patient_id):
    print(patient_id)
    #patients = utils.load_patient()
    patient = utils.get_patient_by_id2(patient_id)
    print(patient)
    if patient:
        return render_template('patient_detail.html', patient=patient)
    else:
        return 'Patient non trouvé'

@app.route('/patients/<int:id>', methods=['GET','PUT', 'DELETE'])
def personne(id):
    conn = sqlite3.connect('dossiers_medicaux.db')
    cursor  = conn.cursor()
    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM patient WHERE id={}".format(id))
        rows = cursor.fetchall()
        for r in rows :
            personne = r
        if personne is not None :
            return jsonify(personne), 200
        else :
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

@app.route("/patientjson/<id>")
def userdata(id):
  document_path = os.getcwd() + '/app/data/Patients/Patient' + id + '.json'
  f = open(document_path, 'r')
  data = json.load(f)
  f.close()
  return data

def immunizationdata(id):
  document_path = os.getcwd() + '/app/static/data/immunization/' + id + '.json'
  f = open(document_path, 'r')
  data = json.load(f)
  f.close()
  return data


@app.route("/patient/<id>")
def patient(id):

    patient = userdata(id)
    return render_template('patient_detail.html', patient=patient)

@app.route("/immunization/<id>")
def immunization(id):

    data = immunizationdata (id)
    return render_template('immunization.html', utilisateur=data)

@app.route('/serv/<id>')
def get_patient_from_server(id):
    url = urllib.request.urlopen('http://172.20.10.2:5000/Patient/'+ id)
    data = json.load(url)
    return render_template('patient_detail.html', patient=data)

camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/visio')
def visio():
    return render_template('visio.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame', headers={'Access-Control-Allow-Origin': '*'})
@app.route('/<name>')
def nom(name):

    return 'Salut! Je pense que tu as fait une erreur dans ta requête : {}'.format(name)

if __name__=='__main':
    app.run(debug=True)