import curses
from app import app
from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3


@app.route('/',methods=['GET'])
def aff_acc_med():
    return render_template('acc_medecin.html')

@app.route('/page_ajout_patient',methods=['GET'])
def page_ajout_patient():
    ajouter_patient
    return render_template('ajout_patient.html')


@app.route('/ajout_patient',methods=['GET'])

def ajouter_patient():
    conn = sqlite3.connect('dossiers_medicaux.db')
    cursor  = conn.cursor()
    nom = request.form["nom"]
    prenom = request.form["prenom"]
    genre = request.form["genre"]
    date = request.form["date"]
    medecin = request.form["medecin"]
    sql = """INSERT INTO patient (nom, prenom, genre)
                VALUES (?, ?, ?, ?, ?)"""
    cursor = cursor.execute(sql, (nom, prenom, genre))
    conn.commit()
    return f"La personne avec id est {cursor.lastrowid} a été ajoutée", 201



@app.route('/rech_patient', methods=['GET'])
def rech_patient():
    return render_template('affiche_patient.html')

@app.route('/patients', methods=['GET', 'POST'])
def affiche_patient():
    conn = sqlite3.connect('dossiers_medicaux.db')
    cursor  = conn.cursor()
    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM dossiers_medicaux")
        patient = [
            dict(id=row[0],nom=row[1],prenom=row[2],genre=row[3],materiel=row[4],recherche=row[5])
            for row in cursor.fetchall()
        ]
        if patient is not None:
            return jsonify(patient)


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


@app.route('/<name>')
def nom(name):

    return 'Salut! Je pense que tu as fait une erreur dans ta requête : {}'.format(name)

if __name__=='__main':
    app.run(debug=True)