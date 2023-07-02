import curses
import urllib

# from fhirclient.models.appointment import Appointment
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from app import app
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
#from app import utils
import json, os
from flask_login import LoginManager, login_user, UserMixin, logout_user, login_required
from flask import flash
from flask_login import current_user
from dateutil.parser import parse
from hl7apy.core import Message
import bcrypt
from serveur_fhir import utils


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TheBDD.db'
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Définition du modèle de l'utilisateur
class Doctors(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))

# Fonction de chargement de l'utilisateur
@login_manager.user_loader
def load_user(user_id):
    return Doctors.query.get(user_id)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Vérification si l'utilisateur existe déjà
        existing_user = Doctors.query.filter_by(username=username).first()
        if existing_user:
            return 'Cet utilisateur existe déjà'

        # Hachage du mot de passe
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        # Création d'un nouvel utilisateur
        new_user = Doctors(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('sign_up.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Recherche de l'utilisateur dans la base de données
        user = Doctors.query.filter_by(username=username).first()
        test=1
        if test == 1 :
            return redirect(url_for('accueil'))

        # Vérification du mot de passe
        if user and bcrypt.checkpw(password, user.password):
            # Authentification réussie
            login_user(user)
            return redirect(url_for('search_practitioners'))
        else:
            # Authentification échouée
            return 'Identifiant ou mot de passe incorrect'

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('accueil'))
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


@app.route("/connexion_medecin", methods=['GET', 'POST'])
def connexion_medecin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Recherche de l'utilisateur dans la base de données
        user = Doctors.query.filter_by(username=username).first()
        #return render_template('acc_medecin.html')
        # Vérification du mot de passe
        if user and password == user.password:
            # Authentification réussie
            login_user(user)
            return redirect(url_for('aff_acc_med'))
        else:
            # Authentification échouée
            return 'Identifiant ou mot de passe incorrect'
    return render_template('connexion_medecin.html')


@app.route('/get_appointments/<int:practitioner_id>')
def get_appointments(practitioner_id):
    conn = sqlite3.connect('theBDD.db')
    c = conn.cursor()
    cur = c.execute('SELECT * FROM appointments WHERE doctor_id = ?', (practitioner_id,))
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
    #return redirect(urllib.request.urlopen('http://0.0.0.0:8000'))
    return render_template('patient_detail.html', patient=patient)


@app.route('/fhir', methods=['GET','POST'])
def aff_acc_med():
    return redirect('http://0.0.0.0:8000/fhir')
    #return render_template('acc_medecin.html')


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
        date_str = date.strftime('%d/%m/%Y')
        #patients = utils.read_json(os.path.join(app.root_path, 'data/Patients/Patient' + str(id) + '.json'))
        # Chemin vers le répertoire où sont stockées les données des patients
        directory = os.path.join(app.root_path, 'data/Patients/')

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

@app.route('/fhir/rech_patient', methods=['GET', 'POST'])
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
    document_path = os.getcwd() + '/app/data/immunization/' + id + '.json'
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
    url = urllib.request.urlopen('http://0.0.0.0:8000/data/Patients/Patient' + id)
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


#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000)

