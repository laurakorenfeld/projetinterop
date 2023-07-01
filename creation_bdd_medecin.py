import sqlite3
import bcrypt
import secrets
import string

def generate_random_password(length=10):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


# Connect to the SQLite database
conn = sqlite3.connect('TheBDD.db')
c = conn.cursor()

#Create the patients table
c.execute('''
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

#Create the doctors table
c.execute('''
CREATE TABLE doctors (
    id INTEGER PRIMARY KEY,
    name TEXT,
    location TEXT,
    specialty TEXT,
    email TEXT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

#Create the appointments table
c.execute('''
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY,
    doctor_id INTEGER,
    patient_id INTEGER,
    appointment_date DATETIME,
    FOREIGN KEY (doctor_id) REFERENCES doctors (id),
    FOREIGN KEY (patient_id) REFERENCES patients (id)
)
''')


# Insert sample data into the practitioners table
doctors = [
    ('Dr. Dupont', 'Paris', 'Cardiologue', 'dr.dupont@example.com', 'dr.dupont', 'D0ct0rP@ss1'),
    ('Dr. Martin', 'Lyon', 'Généraliste', 'dr.martin@example.com', 'dr.martin', 'D0ct0rP@ss2'),
    ('Dr. Durand', 'Marseille', 'Pédiatre', 'dr.durand@example.com', 'dr.durand', 'D0ct0rP@ss3'),
    ('Dr. Moreau', 'Bordeaux', 'Dermatologue', 'dr.moreau@example.com', 'dr.moreau', 'D0ct0rP@ss4'),
    ('Dr. Legrand', 'Toulouse', 'Chirurgien', 'dr.legrand@example.com', 'dr.legrand', 'D0ct0rP@ss5'),
    ('Dr. Petit', 'Nantes', 'Radiologue', 'dr.petit@example.com', 'dr.petit', 'D0ct0rP@ss6'),
    ('Dr. Garnier', 'Lille', 'Orthodontiste', 'dr.garnier@example.com', 'dr.garnier', 'D0ct0rP@ss7'),
    ('Dr. Roux', 'Strasbourg', 'Gastro-entérologue', 'dr.roux@example.com', 'dr.roux', 'D0ct0rP@ss8'),
    ('Dr. Ribeiro', 'Nice', 'Neurologue', 'dr.ribeiro@example.com', 'dr.ribeiro', 'D0ct0rP@ss9'),
    ('Dr. Lemaire', 'Grenoble', 'Ophtalmologiste', 'dr.lemaire@example.com', 'dr.lemaire', 'D0ct0rP@ss10'),
    ('Dr. Fontaine', 'Rennes', 'Psychiatre', 'dr.fontaine@example.com', 'dr.fontaine', 'D0ct0rP@ss11'),
    ('Dr. Chevalier', 'Toulon', 'Pneumologue', 'dr.chevalier@example.com', 'dr.chevalier', 'D0ct0rP@ss12'),
    ('Dr. Brun', 'Angers', 'Néphrologue', 'dr.brun@example.com', 'dr.brun', 'D0ct0rP@ss13'),
    ('Dr. Nguyen', 'Reims', 'Rhumatologue', 'dr.nguyen@example.com', 'dr.nguyen', 'D0ct0rP@ss14'),
    ('Dr. Vincent', 'Montpellier', 'Endocrinologue', 'dr.vincent@example.com', 'dr.vincent', 'D0ct0rP@ss15'),
    ('Dr. Da Silva', 'Tours', 'Oncologue', 'dr.dasilva@example.com', 'dr.dasilva', 'D0ct0rP@ss16'),
    ('Dr. Lambert', 'Dijon', 'Chirurgien plastique', 'dr.lambert@example.com', 'dr.lambert', 'D0ct0rP@ss17'),
    ('Dr. Mercier', 'Brest', 'Allergologue', 'dr.mercier@example.com', 'dr.mercier', 'D0ct0rP@ss18'),
    ('Dr. Girard', 'Le Havre', 'Gynécologue', 'dr.girard@example.com', 'dr.girard', 'D0ct0rP@ss19'),
    ('Dr. Guillaume', 'Saint-Étienne', 'Oto-rhino-laryngologiste', 'dr.guillaume@example.com', 'dr.guillaume', 'D0ct0rP@ss20'),
    ('Dr. Haddad', 'Nîmes', 'Urologue', 'dr.haddad@example.com', 'dr.haddad', 'D0ct0rP@ss21'),
    ('Dr. Fernandez', 'Clermont-Ferrand', 'Orthopédiste', 'dr.fernandez@example.com', 'dr.fernandez', 'D0ct0rP@ss22'),
    ('Dr. Boucher', 'Limoges', 'Hématologue', 'dr.boucher@example.com', 'dr.boucher', 'D0ct0rP@ss23'),
    ('Dr. Lacroix', 'Annecy', 'Cardiologue', 'dr.lacroix@example.com', 'dr.lacroix', 'D0ct0rP@ss24'),
    ('Dr. Schmidt', 'Perpignan', 'Généraliste', 'dr.schmidt@example.com', 'dr.schmidt', 'D0ct0rP@ss25'),
    ('Dr. Garcia', 'Caen', 'Pédiatre', 'dr.garcia@example.com', 'dr.garcia', 'D0ct0rP@ss26'),
]

patients = [
    ('Alice', 'Dubois', 'alice.dubois@example.com', 'alice.dubois', 'Pa$$w0rd1'),
    ('Bruno', 'Lefevre', 'bruno.lefevre@example.com', 'bruno.lefevre', 'Pa$$w0rd2'),
    ('Caroline', 'Bernard', 'caroline.bernard@example.com', 'caroline.bernard', 'Pa$$w0rd3'),
    ('David', 'Leroy', 'david.leroy@example.com', 'david.leroy', 'Pa$$w0rd4'),
    ('Elodie', 'Morel', 'elodie.morel@example.com', 'elodie.morel', 'Pa$$w0rd5'),
    ('François', 'Dupont', 'francois.dupont@example.com', 'francois.dupont', 'Pa$$w0rd6'),
    ('Gaelle', 'Simon', 'gaelle.simon@example.com', 'gaelle.simon', 'Pa$$w0rd7'),
    ('Hugo', 'Fournier', 'hugo.fournier@example.com', 'hugo.fournier', 'Pa$$w0rd8'),
    ('Isabelle', 'Roussel', 'isabelle.roussel@example.com', 'isabelle.roussel', 'Pa$$w0rd9'),
    ('Jean-Pierre', 'Girard', 'jean-pierre.girard@example.com', 'jean-pierre.girard', 'Pa$$w0rd10'),
]

appointments = [
    (1, 1, '2023-04-10 09:00:00'),
    (2, 2, '2023-04-10 10:00:00'),
    (3, 3, '2023-04-10 14:00:00'),
    (4, 4, '2023-04-10 15:00:00'),
    (5, 5, '2023-04-10 16:00:00'),
    (6, 6, '2023-04-11 09:00:00'),
    (7, 7, '2023-04-11 10:00:00'),
    (8, 8, '2023-04-11 14:00:00'),
    (9, 9, '2023-04-11 15:00:00'),
    (10, 10, '2023-04-11 16:00:00'),
    (11, 11, '2023-04-12 09:00:00'),
    (12, 12, '2023-04-12 10:00:00'),
    (13, 13, '2023-04-12 14:00:00'),
    (14, 14, '2023-04-12 15:00:00'),
    (15, 15, '2023-04-12 16:00:00'),
]


# Pensez à hasher les mots de passe avant de les stocker dans la base de données
hashed_patients = []

for patient in patients:
    first_name, last_name, email, username, password = patient
    hashed_password = hash_password(password)
    hashed_patients.append((first_name, last_name, email, username, password))
    c.execute("INSERT INTO patients (first_name, last_name, email, username, password) VALUES (?, ?, ?, ?, ?)", patient)

# Insérez les exemples de patients dans votre table patients

for doctor in doctors :
    name, location, specialty, email, username, password = doctor
    hashed_password = hash_password(password)
    hashed_patients.append((name, email, username, hashed_password))
    c.execute("INSERT INTO doctors (name, location, specialty, email, username, password) VALUES (?, ?, ?, ?, ?, ?)", doctor)

for appointment in appointments :
    doctor_id, patient_id, appointment_date = appointment
    c.execute("INSERT INTO appointments (doctor_id, patient_id, appointment_date) VALUES (?, ?, ?)", appointment)

# Commit the changes and close the connection
conn.commit()
conn.close()

