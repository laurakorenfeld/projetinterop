import json, os
from serveur_fhir import serveur_fhir

def read_json(path):
    with open(path, "r") as f:
        return json.load(f)

def load_patient():
    patients = []
    folder_path = os.path.join(os.getcwd(), 'Documents/Travail/ITS/projetinterop/serveur_fhir/data/Patients')
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        patient_id = len(patients) +1
        with open(file_path, 'r') as f:
            patient_data = json.load(f)

            patient = {
                'identifier': patient_id,  # use the extracted patient_id here
                'name': patient_data['name'][0]['given'][0] + ' ' + patient_data['name'][0]['family'],
                'birthDate': patient_data['birthDate']
            }
            patients.append(patient)
    return patients

def get_patient_by_id(patient_id):
    patients = read_json(os.path.join(serveur_fhir.root_path, 'data/Patients/Patient' + str(patient_id) + '.json'))
    for p in patients:
        if p['identifier'] == patient_id:
            return p


def get_patient_by_id2(patient_id):
    #compte_fichiers("data/Patients")
    patient = read_json(os.path.join(serveur_fhir.root_path, 'data/Patients/Patient'+str(patient_id)+'.json'))
    return patient

