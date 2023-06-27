import curses
import urllib

#from fhirclient.models.appointment import Appointment
from flask_sqlalchemy import SQLAlchemy

from app import app
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from app import utils
import json, os
from dateutil.parser import parse
from hl7apy.core import Message
import bcrypt

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rendezvous.db'
db = SQLAlchemy(app)

'''
Routes basiques
'''


@app.route("/")
def accueil():
    return render_template('index_vrai.html')


@app.route("/apropos")
def apropos():
    return render_template('apropos.html')


@app.route('/search_practitioners', methods=['POST', 'GET'])
def search_practitioners():
    conn = sqlite3.connect('theBDD.db')
    c = conn.cursor()
    if request.method == 'GET':
        c.execute("SELECT * FROM doctors")

        results = c.fetchall()
        print(results)
        conn.close()
        return render_template('resultat_rech_medecin.html', practitioners=results)

    specialty = request.form['specialty']
    location = request.form['location']

    if specialty == '':
        c.execute("SELECT * FROM doctors WHERE location LIKE ?", ('%' + location + '%',))
    elif location == '':
        c.execute("SELECT * FROM doctors WHERE specialty LIKE ?", ('%' + specialty + '%',))
    else:
        c.execute("SELECT * FROM doctors WHERE specialty LIKE ? AND location LIKE ?",
                  ('%' + specialty + '%', '%' + location + '%'))

    results = c.fetchall()
    conn.close()
    return render_template('resultat_rech_medecin.html', practitioners=results)


@app.route("/connexion_medecin")
def connexion_medecin():
    return render_template('connexion_medecin.html')

@app.route('/infos_medecin/<int:practitioner_id>')

def infos_medecin(practitioner_id):

    conn = sqlite3.connect('theBDD.db')
    c = conn.cursor()
    cur = c.execute('SELECT * FROM appointments WHERE doctor_id = ?', (practitioner_id,))
    appointments = cur.fetchall()

    # Organize the appointments by day and hour for easy display
    appointment_schedule = {"Lundi": [], "Mardi": [], "Mercredi": [], "Jeudi": [], "Vendredi": []}
    days_in_french = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    for appointment in appointments:
        date_str = str(appointment[3])
        print(date_str)
        day = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').strftime('%d')
        if day in appointment_schedule:
            appointment_schedule[day].append((appointment[1], appointment[2], date_str))

    conn.close()
    # Pass the appointments to the template
    return render_template('infos_medecin.html', appointments=appointment_schedule)

@app.route('/get_appointments')
def get_appointments():
    conn = sqlite3.connect('theBDD.db')
    c = conn.cursor()
    cur = c.execute('SELECT * FROM appointments')
    appointments = cur.fetchall()
    conn.close()

    # Format appointments in the format expected by FullCalendar
    events = []
    for appointment in appointments:
        events.append({
            'title': 'Appointment with patient {}'.format(appointment[2]),
            'start': appointment[3],
            'allDay': False
        })

    return jsonify(events)


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
    return jsonify(metadata)

@app.route("/fhir/Patient")
def patient_list():
    patients = utils.load_patient()
    return render_template('patient.html', patients=patients)
    # return patients


@app.route("/fhir/Patient/<int:patient_id>")
def patient_details(patient_id):
    patient = utils.get_patient_by_id(patient_id)
    return render_template('patient_detail.html', patient=patient)


@app.route('/fhir', methods=['GET'])
def aff_acc_med():
    return render_template('acc_medecin.html')


@app.route('/fhir/page_ajout_patient', methods=['GET', 'POST'])
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
        id = 2
        date_str = date.strftime('%d/%m/%Y')
        patients = utils.read_json(os.path.join(app.root_path, 'data/Patients/Patient' + str(id) + '.json'))

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

        with open(os.path.join(app.root_path, 'data/Patients/patient' + id + '.json'), 'w') as f:
            json.dump(patients, f)

        return redirect(url_for('patient_list'))


@app.route('/fhir/rech_patient', methods=['GET', 'POST'])
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
    # patients = utils.load_patient()
    patient = utils.get_patient_by_id2(patient_id)
    print(patient)
    if patient:
        return render_template('patient_detail.html', patient=patient)
    else:
        return 'Patient non trouvé'


@app.route('/patients/<int:id>', methods=['GET', 'PUT', 'DELETE'])
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
    data = immunizationdata(id)
    return render_template('immunization.html', utilisateur=data)


@app.route('/serv/<id>')
def get_patient_from_server(id):
    url = urllib.request.urlopen('http://172.20.10.2:5000/Patient/' + id)
    data = json.load(url)
    return render_template('patient_detail.html', patient=data)


class RendezVous(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10), nullable=False)
    heure = db.Column(db.String(5), nullable=False)
    medecin = db.Column(db.String(50), nullable=False)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.String(200), nullable=False)


@app.route('/page_patient/prendre_rendezvous', methods=['POST'])
def prendre_rendezvous():
    date = request.form['date']
    heure = request.form['heure']
    medecin = request.form['medecin']
    nom = request.form['nom']
    prenom = request.form['prenom']
    email = request.form['email']
    telephone = request.form['telephone']
    message = request.form['message']
    rdv = RendezVous(date=date, heure=heure, medecin=medecin, nom=nom, prenom=prenom, email=email, telephone=telephone,
                     message=message)
    db.session.add(rdv)
    db.session.commit()
    return redirect('/page_patient/rdv')


@app.route('/page_patient/calendrier')
def calendrier():
    # Déterminer la semaine en cours
    debut_semaine = datetime.now().date() - timedelta(days=datetime.now().weekday())
    fin_semaine = debut_semaine + timedelta(days=6)
    # Récupérer les rendez-vous pour la semaine en cours
    rendezvous = RendezVous.query.filter(RendezVous.date >= debut_semaine.strftime('%Y-%m-%d')).filter(
        RendezVous.date <= fin_semaine.strftime('%Y-%m-%d')).all()
    # Préparer les données à envoyer au template HTML
    events = []
    for rdv in rendezvous:
        start_time = datetime.strptime(f"{rdv.date} {rdv.heure}", "%Y-%m-%d %H:%M")
        end_time = start_time + timedelta(minutes=30)  # Durée du rendez-vous = 30 minutes
        event = {
            'title': f"{rdv.nom} {rdv.prenom}",
            'start': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'backgroundColor': '#ffc107',
            'borderColor': '#ffc107',
            'textColor': '#212529',
        }
        events.append(event)
    # Afficher le calendrier
    return render_template('rdv.html', events=events)


@app.route('/page_patient/rdv')
def page_rdv():
    return render_template('rdv.html')

@app.route('/monchat')
def chatetvideo():
    return redirect("http://127.0.0.1:3000/mon-chat-video/accueil-salle.html", code=302)

@app.route('/<name>')
def nom(name):
    return 'Salut! Je pense que tu as fait une erreur dans ta requête : {}'.format(name)


if __name__ == '__main':
    app.run(debug=True)
