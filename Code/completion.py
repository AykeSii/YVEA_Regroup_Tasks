# Remplissage des PDFs pour chaque ligne de données
from fillpdf import fillpdfs
import os

class Completion:
    def generate_pdf(record, input_pdf_path='testForm.pdf', output_folder='filled_pdfs'):
        os.makedirs(output_folder, exist_ok=True)
        form_fields = list(fillpdfs.get_form_fields(input_pdf_path).keys())
        
        # Création d'un dictionnaire pour le mappage des champs du formulaire aux données
        data_dict = {}
        for field in form_fields:
            if 'id' in field.lower():
                data_dict[field] = record.get('id', 'null')
            if 'name' in field.lower():
                data_dict[field] = record.get('name', 'null')
            elif 'surname' in field.lower():
                data_dict[field] = record.get('surname', 'null')
            elif 'address' in field.lower():
                data_dict[field] = record.get('address', 'null')
            elif 'email' in field.lower():
                data_dict[field] = record.get('email', 'null')
            elif 'age' in field.lower():
                data_dict[field] = record.get('age', 'null')
            elif 'profession' in field.lower():
                data_dict[field] = record.get('profession', 'null')
            elif 'status' in field.lower():
                data_dict[field] = record.get('status', 'null')
            elif 'telephone' in field.lower():
                data_dict[field] = record.get('telephone', 'null')

        output_pdf_path = os.path.join(output_folder, f"{record.get('name', 'output')}_filled.pdf")
        fillpdfs.write_fillable_pdf(input_pdf_path, output_pdf_path, data_dict)