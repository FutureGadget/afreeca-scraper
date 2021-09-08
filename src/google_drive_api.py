from google_cred import get_cred
from googleapiclient.discovery import build
from googleapiclient import errors
from googleapiclient.http import MediaFileUpload

client_secrets_file = './secrets/client_secret_145861033977-k4oc4je2bmg8ai4undjd7190bebqm69i.apps.googleusercontent.com.json'
scopes = ['https://www.googleapis.com/auth/drive']

def save(title, filename):
    creds = get_cred(client_secrets_file, scopes)
    service = build('drive', 'v3', credentials=creds, cache_discovery=False)
    return insert_file(service, title, '1bE-A_oYEyRjsBJZrKGrgeNLNrzktwR87', 'video/mpeg', filename)

def insert_file(service, title, parent_id, mime_type, filename):
    media = MediaFileUpload(filename, mimetype=mime_type, resumable=True)
    file_metadata = {
        'name': title
    }# Set the parent folder.
    if parent_id:
        file_metadata['parents'] = [parent_id]

    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id').execute()

        # Uncomment the following line to print the File ID
        print(f"File ID: {file.get('id')}")

        return file
    except errors.HttpError as error:
        print(f'An error occured: {error}')
        return None

if __name__ == '__main__':
    save('test.mpeg', './1630973857.mpeg')
