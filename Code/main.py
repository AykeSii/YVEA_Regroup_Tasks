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
api_key = os.getenv('AIRTABLE_API_KEY')  # Assure-toi de stocker ta clé API dans le fichier .env
base_id = 'appRw31lR2vRnbmZh'
table_name = 'tbl1SB4jobmAWKC9j'

# URL de l'API Airtable
endpoint = f'https://api.airtable.com/v0/{base_id}/{table_name}'

# En-têtes pour l'authentification
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Recherche un enregistrement par ID dans Airtable pour voir si celui-ci existe déjà.
def search_registration(data):
    filter_formula = f"{{ID}} = '{data['id']}'"  # Crée une formule de filtrage pour l'API.
    query_params = {'filterByFormula': filter_formula}
    response = requests.get(endpoint, headers=headers, params=query_params)  # Effectue la requête GET.
    response.raise_for_status()
    records = response.json().get('records', []) 
    return records[0]['id'] if records else None

# Met à jour un enregistrement existant dans Airtable avec les nouvelles données fournies.
def update_registration(record_id, data):
    update_endpoint = f"{endpoint}/{record_id}"
    try:
        response = requests.patch(update_endpoint, headers=headers, json={'fields': data})  # Effectue la requête PATCH.
        response.raise_for_status()
        print("Data updated.")
        return response.json() 
    except requests.RequestException as e:
        print(f"Registration update error: {e}")
        return None

# Ajoute un nouvel enregistrement dans Airtable avec les données fournies.
def add_registration(data):
    try:
        response = requests.post(endpoint, headers=headers, json={'fields': data})  # Effectue la requête POST.
        response.raise_for_status()
        print("New registration added.")
        return response.json() 
    except requests.RequestException as e:
        print(f"Error adding record: {e}")
        return None

# Détermine si un enregistrement doit être ajouté ou mis à jour en fonction de son existence dans Airtable.
def add_or_update(data):
    record_id = search_registration(data)  # Recherche l'ID de l'enregistrement existant.
    if record_id:
        return update_registration(record_id, data)
    else:
        return add_registration(data)

# Fonction pour créer et retourner un dictionnaire JSON structuré
def create_json_structure(input_text):
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
        return None

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
    pdf_file_path = "Documents/Formulaire_remplie_cris2.pdf"
    tasks = Tasks(agents.pdf_reader, agents.article_writer, agents.data_manager, pdf_file_path)

    crew = Crew(agents=[agents.pdf_reader, agents.article_writer, agents.data_manager], tasks=[tasks.task_read_pdf, tasks.task_format_json, tasks.task_avoid_duplication], verbose=2)
    result = crew.kickoff()

    structured_data = create_json_structure(result)
    if structured_data:
        add_or_update(structured_data)
        user_defined_filename = input("How do you want to name the file? (don't add an extension): ")
        destination_path = f"Informations_extracts/{user_defined_filename}.json"
        create_json_file(structured_data, destination_path)
        
        xlsx_path = f"Excel_extracts/{user_defined_filename}.xlsx"
        json_to_xlsx(destination_path, xlsx_path)

        # Traitement du fichier Excel et envoi à Airtable
        process_excel_and_post()
    else:
        print("No valid data to add to Airtable or save locally.")