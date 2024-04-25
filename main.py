from dotenv import load_dotenv
from crewai import Crew
import os
import json
from tasks import Tasks
from agents import Agents

# Chargez votre OPENAI_API_KEY à partir de votre fichier .env
load_dotenv()

# Fonction pour créer un fichier JSON à un emplacement spécifique
def create_json_file(input_text, output_json_path):
    # Créez un dictionnaire avec les données à sauvegarder
    data = {
        "text": input_text
    }
    
    # Vérifiez si le répertoire existe, sinon, créez-le
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    
    # Écrivez le dictionnaire dans un fichier JSON à l'emplacement spécifié
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

# Exécution principale
if __name__ == "__main__":
    agents = Agents()
    pdf_file_path = "Documents/facture1.pdf"  # Spécifiez le chemin
    tasks = Tasks(agents.pdf_reader, agents.article_writer, pdf_file_path)

    # Instanciez et exécutez l'équipage
    crew = Crew(
        agents=[agents.pdf_reader, agents.article_writer],
        tasks=[tasks.task_read_pdf, tasks.task_format_json],
        verbose=2
    )

    # Exécutez l'équipage et gérez les résultats correctement
    result = crew.kickoff()

    # Demandez à l'utilisateur le nom de fichier souhaité
    user_defined_filename = input("Comment voulez-vous nommer le fichier ? (ne pas ajouter d'extension) : ")

    # Spécifiez l'emplacement exact où vous souhaitez que le fichier soit créé
    destination_path = f"Informations_extracts/{user_defined_filename}.json"

    # Sauvegardez le résultat dans un fichier JSON
    create_json_file(result, destination_path)