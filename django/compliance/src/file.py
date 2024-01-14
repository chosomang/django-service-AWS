from ..models import Document
import mimetypes
import docx2pdf
from aspose.slides import Presentation

def get_file_preivew_details(request):
    documents = Document.objects.filter(title=request.POST.get('comment', ''))
    for document in documents:
        if document.uploadedFile.name.endswith(request.POST.get('name', '').replace('[','').replace(']','')):
            mime_type, _ = mimetypes.guess_type(document.uploadedFile.path)
            file_url = document.uploadedFile.url
            file_path = document.uploadedFile.path
            if mime_type is None:
                mime_type = 'image/png'
            elif 'docx' in mime_type:
                file_url, mime_type = docx_to_pdf(file_path, file_url)
            elif 'ppt' in mime_type:
                file_url, mime_type = ppt_to_img(file_path, file_url)
    print(file_url)
    print(mime_type)
    return file_url, mime_type

def docx_to_pdf(file_path, file_url):
    preview_path = '\\'.join(file_path.split('\\')[:-1])+'\\preview.pdf'
    preview_url = '/'.join(file_url.split('/')[:-1]) + '/preview.pdf'
    docx2pdf.convert(file_path, preview_path)
    return preview_url, 'application/pdf'

def ppt_to_img(file_path, file_url):
    presentation = Presentation(file_path)
    for slide in presentation.slides:
        image_path = '\\'.join(file_path.split('\\')[:-1])+'\\preview.png'
        print(image_path)
        print(slide)
        slide.get_thumbnail().save(image_path)
        break
    preview_url = '/'.join(file_url.split('/')[:-1]) + '/preview.png'
    return preview_url, 'image/png'