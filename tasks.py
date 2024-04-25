from crewai import Task

# Tasks
class Tasks:
    def __init__(self, pdf_reader, article_writer, pdf_file_path):
        self.pdf_reader = pdf_reader
        self.article_writer = article_writer
        self.pdf_file_path = pdf_file_path
        self.task_read_pdf = Task(
            description=f"Read and preprocess the text from the PDF at this path: {self.pdf_file_path}",
            expected_output="Text of the PDF",
            agent=self.pdf_reader
        )
        self.task_format_json = Task(
            description="Extract key information from the PDF document and format it into a structured JSON.",
            expected_output="Formatted JSON",
            agent=self.article_writer
        )
