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
        patient_id = int(filename.replace("Patient", "").replace(".json", ""))  # extract patient id from filename
        with open(file_path, 'r') as f:
            patient_data = json.load(f)

            patient = {
                'identifier': patient_id,  # use the extracted patient_id here
                'name': patient_data['name'][0]['given'][0] + ' ' + patient_data['name'][0]['family'],
                'birthDate': patient_data['birthDate']
            }
            patients.append(patient)
    return sorted(patients, key=lambda k: k['identifier'])  # ensure patients are sorted by identifier


def get_patient_by_id(patient_id):
    patients = read_json(os.path.join(serveur_fhir.root_path, 'data/Patients/Patient' + str(patient_id) + '.json'))
    for p in patients:
        if p['identifier'] == patient_id:
            return p


def get_patient_by_id2(patient_id):
    #compte_fichiers("data/Patients")
    patient = read_json(os.path.join(serveur_fhir.root_path, 'data/Patients/Patient'+str(patient_id)+'.json'))
    return patient

def get_next_patient_id():
    folder_path = os.path.join(os.getcwd(), 'Documents/Travail/ITS/projetinterop/serveur_fhir/data/Patients')
    files = os.listdir(folder_path)
    json_files = [file for file in files if file.endswith('.json')]
    new_id = len(json_files) + 1
    return new_id
def update_patient(patient_id, updated_patient):
    file_path = os.path.join(serveur_fhir.root_path, 'data/Patients/Patient' + str(patient_id) + '.json')
    if os.path.exists(file_path):
        with open(file_path, 'r+') as f:
            patient_data = json.load(f)
            # Effectuer les mises à jour des champs du patient avec les valeurs de updated_patient
            patient_data['name'][0]['given'][0] = updated_patient['prenom']
            patient_data['name'][0]['family'] = updated_patient['nom']
            patient_data['gender'] = updated_patient['genre']
            f.seek(0)
            json.dump(patient_data, f, indent=4)
            f.truncate()
    else:
        raise FileNotFoundError("Patient not found.")

def delete_patient(patient_id):
    file_path = os.path.join(serveur_fhir.root_path, 'data/Patients/Patient' + str(patient_id) + '.json')
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        raise FileNotFoundError("Patient not found.")
