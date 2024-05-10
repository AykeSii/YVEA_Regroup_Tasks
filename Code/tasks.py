from crewai import Task

# Tasks
class Tasks:
    def __init__(self, pdf_reader, article_writer, data_manager, pdf_file_path):
        self.pdf_reader = pdf_reader
        self.article_writer = article_writer
        self.data_manager = data_manager
        self.pdf_file_path = pdf_file_path
        self.task_read_pdf = Task(
            description=f"Read and preprocess the text from the PDF at this path: {self.pdf_file_path}",
            expected_output="""Text of the PDF.
            If the information is not written in the document, return "null".""",
            agent=self.pdf_reader
        )
        self.task_format_json = Task(
            description=f"""Extract the following information: 
            { 
                "id", 
                "name",
                "surname", 
                "age",
                "profession", 
                "status", 
                "address", 
                "email", 
                "telephone" 
            } 
            from the PDF document and format it in a structured JSON.""",

            expected_output="""Formatted JSON.
            Important: the list must not contain any unspecified information. If any information is missing, write "null". 
            Each piece of information must be written on a different line from the others. If there are several different pieces 
            of information in the same document, sort the information intelligently and display the result in the same file. 
            If there is the same information in a document, the result JSON file MUST be structured exactly as shown in the "Example Output", you can't use or add another structure.            
            Example Output:
            {
                "id": ""<generated_id>"",
                "name": "<generated_name>",
                "surname": "<generated_surname>",
                "age": <generated_age>,
                "profession": "<generated_profession>",
                "status": "<generated_status>",
                "address": "<generated_address>",
                "email": "<generated_email>",
                "telephone": "<generated_telephone>"
            }
            Gives the result of the JSON file to "data_manager" without modifying the structure of the file.
            """,
            agent=self.article_writer
        )
        self.task_avoid_duplication = Task(
            description="""Read the rendering of the "article_writer" agent and avoid duplication of information, if any.""",
            expected_output="""Unduplicated data.
            Important: If the data contains duplicates, you must delete the duplicates so that the data appears only once.
            IMPORTANT : You can't edit the structure of the JSON file.
            """,
            agent=self.data_manager
        )