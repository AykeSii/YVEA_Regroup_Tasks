from dotenv import load_dotenv
import os
import json
import pandas as pd
import requests

from crewai import Crew
from tasks import Tasks
from agents import Agents

# Chargez votre OPENAI_API_KEY à partir de votre fichier .env
load_dotenv()

# Exemple d'utilisation de la fonction fetch_from_airtable
api_key = os.getenv('AIRTABLE_API_KEY')
base_id = 'appRw31lR2vRnbmZh'
table_name = 'tbl1SB4jobmAWKC9j'

# URL de l'API Airtable
endpoint = f'https://api.airtable.com/v0/{base_id}/{table_name}'

# En-têtes pour l'authentification
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

id_field = "id"

def retrieve_records():
    response = requests.get(endpoint, headers=headers)
    response.raise_for_status()
    records = response.json().get('records', [])
    return records

def update_records(records, fields_to_check):
    updated_records = []
    for record in records:
        existing_id = search_registration({'id': record['id']})
        if existing_id:
            updated_record = update_registration(existing_id, record['fields'], fields_to_check)
            updated_records.append(updated_record)
    return updated_records

def search_registration(data):
    filter_formula = f"{{ID}} = '{data['id']}'"
    query_params = {'filterByFormula': filter_formula}
    response = requests.get(endpoint, headers=headers, params=query_params)
    response.raise_for_status()
    records = response.json().get('records', [])
    return records[0]['id'] if records else None

def update_registration(record_id, data, fields_to_check):
    update_endpoint = f"{endpoint}/{record_id}"
    fields_to_fill = {}
    
    # print("Data received for update:", data)
    # print("Fields to check for missing info:", fields_to_check)
    
    for field in fields_to_check:
        # Ajouter une vérification pour la chaîne 'null' en plus de vérifier si le champ est manquant ou vide
        if field not in data or not data[field] or data[field] == 'null':
            print(f"The element '{field}' is missing.")
            missing_value = input(f"Please enter the value for '{field}' : ")
            fields_to_fill[field] = missing_value

    if fields_to_fill:
        data.update(fields_to_fill)
        # print("Updated data with user inputs:", data)

    try:
        response = requests.patch(update_endpoint, headers=headers, json={'fields': data})
        response.raise_for_status()
        print("Data updated successfully.")
        return response.json()
    except requests.RequestException as e:
        print(f"Registration update error: {e}")
        return None
    
    try:
        response = requests.patch(update_endpoint, headers=headers, json={'fields': data})
        response.raise_for_status()
        print("Data updated successfully.")
        return response.json()
    except requests.RequestException as e:
        print(f"Registration update error: {e}")
        return None


def add_registration(data):
    try:
        response = requests.post(endpoint, headers=headers, json={'fields': data})
        response.raise_for_status()
        print("New registration added.")
        return response.json() 
    except requests.RequestException as e:
        print(f"Error adding record: {e}")
        return None

def add_or_update(data, fields_to_check):
    record_id = search_registration(data)
    if record_id:
        return update_registration(record_id, data, fields_to_check)
    else:
        return add_registration(data)

# Fonction pour créer et retourner un dictionnaire JSON structuré
def create_json_structure(input_text):
    while True:
        try:
            data = json.loads(input_text)
            structured_data = {
                "id": data.get("id", "null"),
                "name": data.get("name", "null"),
                "surname": data.get("surname", "null"),
                "age": data.get("age", "null"),
                "profession": data.get("profession", "null"),
                "status": data.get("status", "null"),
                "address": data.get("address", "null"),
                "email": data.get("email", "null"),
                "telephone": data.get("telephone", "null")
            }
            return structured_data
        except json.JSONDecodeError as e:
            print(f"JSON formatting error: {e}")
            # Ici, on ne retourne rien et donc la boucle continue

# Fonction pour créer un fichier JSON
def create_json_file(data, output_json_path):
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# Fonction pour convertir un fichier JSON en XLSX
def json_to_xlsx(json_path, xlsx_path):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    df = pd.DataFrame([data])
    df.to_excel(xlsx_path, index=False)

# Lecture du fichier Excel, conversion en JSON, et POST des données à Airtable
def process_excel_and_post():
    # Lecture du dernier fichier Excel créé, conversion en JSON, et POST des données à Airtable
    excel_directory = 'Excel_extracts'
    files = [os.path.join(excel_directory, f) for f in os.listdir(excel_directory) if f.endswith('.xlsx')]
    latest_file = max(files, key=os.path.getmtime)

    df = pd.read_excel(latest_file)
    parsed = df.to_dict(orient="records")

# Exécution principale
if __name__ == "__main__":
    agents = Agents()
    fields_to_check = ["id", "name", "surname", "age", "profession", "status", "address", "email", "telephone"]  # Liste des champs à vérifier pour les informations manquantes
    pdf_file_path = "Documents/Formulaire_remplie_cris2.pdf"
    tasks = Tasks(agents.pdf_reader, agents.article_writer, agents.data_updater, agents.data_manager, pdf_file_path)

    crew = Crew(agents=[agents.pdf_reader, agents.article_writer, agents.data_updater, agents.data_manager], tasks=[tasks.task_read_pdf, tasks.task_format_json, tasks.task_data_update, tasks.task_avoid_duplication], verbose=2)
    result = crew.kickoff()

    structured_data = create_json_structure(result)

    records = retrieve_records()
    if records:
        updated_records = update_records(records, fields_to_check)

    if structured_data:
        add_or_update(structured_data, fields_to_check)
        user_defined_filename = input("How do you want to name the file? (don't add an extension): ")
        destination_path = f"Informations_extracts/{user_defined_filename}.json"
        create_json_file(structured_data, destination_path)

        xlsx_path = f"Excel_extracts/{user_defined_filename}.xlsx"
        json_to_xlsx(destination_path, xlsx_path)

        # Traitement du fichier Excel et envoi à Airtable
        process_excel_and_post()
    else:
        print("No valid data to add to Airtable or save locally.")