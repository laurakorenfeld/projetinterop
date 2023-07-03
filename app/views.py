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


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TheBDD1.db'
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
    conn = sqlite3.connect('/Users/LKorenfeld/Documents/Travail/ITS/projetinterop/TheBDD.db')
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
@app.route('/infos_medecin/<int:practitioner_id>')
def infos_medecin(practitioner_id):

    conn = sqlite3.connect('/Users/LKorenfeld/Documents/Travail/ITS/projetinterop/TheBDD.db')
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

@app.route('/fhir', methods=['GET','POST'])
def aff_acc_med():
    return redirect('http://0.0.0.0:8000/fhir')
    #return render_template('acc_medecin.html')


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


