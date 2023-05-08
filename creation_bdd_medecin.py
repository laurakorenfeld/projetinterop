import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('telemedecine.db')
c = conn.cursor()

#Create the practitioners table
c.execute('''
CREATE TABLE practitioners (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    specialty TEXT NOT NULL
)
''')

# Insert sample data into the practitioners table
practitioners = [
    ('Dr. Dupont', 'Paris', 'Cardiologue'),
    ('Dr. Martin', 'Lyon', 'Généraliste'),
    ('Dr. Durand', 'Marseille', 'Pédiatre'),
    ('Dr. Moreau', 'Bordeaux', 'Dermatologue'),
    ('Dr. Legrand', 'Toulouse', 'Chirurgien'),
    ('Dr. Petit', 'Nantes', 'Radiologue'),
    ('Dr. Garnier', 'Lille', 'Orthodontiste'),
    ('Dr. Roux', 'Strasbourg', 'Gastro-entérologue'),
    ('Dr. Ribeiro', 'Nice', 'Neurologue'),
    ('Dr. Lemaire', 'Grenoble', 'Ophtalmologiste'),
    ('Dr. Fontaine', 'Rennes', 'Psychiatre'),
    ('Dr. Chevalier', 'Toulon', 'Pneumologue'),
    ('Dr. Brun', 'Angers', 'Néphrologue'),
    ('Dr. Nguyen', 'Reims', 'Rhumatologue'),
    ('Dr. Vincent', 'Montpellier', 'Endocrinologue'),
    ('Dr. Da Silva', 'Tours', 'Oncologue'),
    ('Dr. Lambert', 'Dijon', 'Chirurgien plastique'),
    ('Dr. Mercier', 'Brest', 'Allergologue'),
    ('Dr. Girard', 'Le Havre', 'Gynécologue'),
    ('Dr. Guillaume', 'Saint-Étienne', 'Oto-rhino-laryngologiste'),
    ('Dr. Haddad', 'Nîmes', 'Urologue'),
    ('Dr. Fernandez', 'Clermont-Ferrand', 'Orthopédiste'),
    ('Dr. Boucher', 'Limoges', 'Hématologue'),
    ('Dr. Lacroix', 'Annecy', 'Cardiologue'),
    ('Dr. Schmidt', 'Perpignan', 'Généraliste'),
    ('Dr. Garcia', 'Caen', 'Pédiatre'),
]

for practitioner in practitioners:
    c.execute("INSERT INTO practitioners (name, location, specialty) VALUES (?, ?, ?)", practitioner)

# Commit the changes and close the connection
conn.commit()
conn.close()