import json, os
from app import app

def read_json(path):
    with open(path, "r") as f:
        return json.load(f)

def load_patient():
    patients = read_json(os.path.join(app.root_path, 'data/Patients/patient.json'))
    return patients

def get_patient_by_id(patient_id):
    patients = read_json(os.path.join(app.root_path, 'data/Patients/Patient' + str(patient_id) + '.json'))
    for p in patients:
        if p['identifier'] == patient_id:
            return p


def get_patient_by_id2(patient_id):
    compte_fichiers("data/Patients")
    patient = read_json(os.path.join(app.root_path, 'data/Patients/Patient'+patient_id+'.json'))
    return patient

def compte_fichiers(path) :
    files = os.listdir(path)
    n = 0
    for file in files:
        if os.path.isfile(os.path.join(path, file)):
            n += 1

