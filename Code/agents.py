from crewai import Agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool
import re
from dotenv import load_dotenv
from pdfminer.high_level import extract_text

# Chargez votre OPENAI_API_KEY à partir de votre fichier .env
load_dotenv()

# Choisissez le modèle pour les agents
model = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0.2)

# Outil pour récupérer et prétraiter le contenu PDF
@tool
def fetch_pdf_content(file_path: str) -> str:
    """
    Opens and preprocesses content from a PDF given its file path.
    Returns the text of the PDF.
    """
    text = extract_text(file_path)
    processed_text = re.sub(r'\s+', ' ', text).strip()
    return processed_text

# Agents
class Agents:
    def __init__(self):
        self.pdf_reader = Agent(
            role='PDF Content Extractor',
            goal='Extract and preprocess text from a PDF',
            backstory='Specializes in handling and interpreting PDF documents',
            verbose=True,
            tools=[fetch_pdf_content],
            allow_delegation=False,
            llm=model
        )

        self.article_writer = Agent(
            role='PDF Writer',
            goal="""Use extracted text to gather and format information in a line-by-line structured JSON file.
            Gives the result of the JSON file to "data_manager" without modifying the structure of the file
            """,
            backstory='Expert in creating informative and structured outputs.',
            verbose=True,
            allow_delegation=False,
            llm=model
        )

        self.data_updater = Agent(
            role='Data Updater',
            goal="""First, query the AirTable API to find the fields where "null" is written. 
            Secondly, asks the user to fill in the "null" fields and update the database.
            """,
            backstory='Expert in data recovery and updating.',
            verbose=True,
            allow_delegation=False,
            llm=model
        )

        self.data_manager = Agent(
            role='Data Manager',
            goal="""Check that the data to be imported into AirTable or a JSON file is not duplicated, if there are any.
            IMPORTANT : You can't edit the structure of the JSON file.
            """,
            backstory='Expert to avoid duplication of data and not to modify the files.',
            verbose=True,
            allow_delegation=False,
            llm=model
        )

        self.pdf_generator = Agent(
            role='PDF Generator',
            goal="""Generate new filled PDF files, based on database data.
            """,
            backstory='Expert to generate PDF files.',
            verbose=True,
            allow_delegation=False,
            llm=model
        )