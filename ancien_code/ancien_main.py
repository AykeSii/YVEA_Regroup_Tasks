# from dotenv import load_dotenv
# from crewai import Agent, Task, Crew
# from langchain_openai import ChatOpenAI
# from langchain.tools import tool
# from PyPDF2 import PdfReader, PdfWriter
# import re
# import os
# import json

# # Load your OPENAI_API_KEY from your .env file
# load_dotenv()

# # Choose the model for the agents
# model = ChatOpenAI(model_name="gpt-4-1106-preview", temperature=0.2)

# # Tool to fetch and preprocess PDF content
# @tool
# def fetch_pdf_content(file_path: str) -> str:
#     """
#     Opens and preprocesses content from a PDF given its file path.
#     Returns the text of the PDF.
#     """
#     with open(file_path, 'rb') as f:
#         pdf = PdfReader(f)
#         text = '\n'.join(page.extract_text() for page in pdf.pages if page.extract_text())
#     processed_text = re.sub(r'\s+', ' ', text).strip()
#     return processed_text

# # Function to create a JSON file at a specific destination
# def create_json_file(input_text, output_json_path):
#     # Create a dictionary with the data to be saved
#     data = {
#         "text": input_text
#     }
    
#     # Check if the directory exists, if not, create it
#     os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    
#     # Write the dictionary to a JSON file at the specified destination
#     with open(output_json_path, 'w', encoding='utf-8') as json_file:
#         json.dump(data, json_file, ensure_ascii=False, indent=4)

# # Agents
# pdf_reader = Agent(
#     role='PDF Content Extractor',
#     goal='Extract and preprocess text from a PDF',
#     backstory='Specializes in handling and interpreting PDF documents',
#     verbose=True,
#     tools=[fetch_pdf_content],
#     allow_delegation=False,
#     llm=model
# )

# article_writer = Agent(
#     role='PDF Writer',
#     goal='Use extracted text to gather and format information in a JSON file.',
#     backstory='Expert in creating informative and structured outputs.',
#     verbose=True,
#     allow_delegation=False,
#     llm=model
# )

# # Tasks
# pdf_file_path = "CV_Cristiano_2024_Alternance.pdf"  # Specify the path

# # Read and preprocess the text from the PDF
# pdf_text = fetch_pdf_content(pdf_file_path)

# task_read_pdf = Task(
#     description=f"Read and preprocess the text from the PDF at this path: {pdf_file_path}",
#     expected_output="Text of the PDF",
#     agent=pdf_reader
# )

# task_format_json = Task(
#     description="Extract key information from the PDF document and format it into a structured JSON.",
#     expected_output="Formatted JSON",
#     agent=article_writer
# )

# # Instantiate and run the crew
# crew = Crew(
#     agents=[pdf_reader, article_writer],
#     tasks=[task_read_pdf, task_format_json],
#     verbose=2
# )

# # Execute the crew and handle results properly
# result = crew.kickoff()

# # Ask user for the desired file name
# user_defined_filename = input("Comment voulez-vous nommer le fichier ? (n'ajoutez pas d'extension): ")

# # Specify the exact destination where you want the file to be created
# destination_path = f"Informations_extracts/{user_defined_filename}.json"

# # Save the result to a JSON file
# create_json_file(result, destination_path)