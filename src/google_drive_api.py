from googleapiclient import errors
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from constants import VIDEO_DIR
from gmail import broadcast_to_enrolled_users
from google_cred import get_cred


def savdAndBroadcastEmail(title, filename):
    creds = get_cred()
    service = build('drive', 'v3', credentials=creds)
    return insert_file(service, title, '1bE-A_oYEyRjsBJZrKGrgeNLNrzktwR87', 'video/mpeg', filename)

def get_file_link(fileId):
    return f"https://drive.google.com/file/d/{fileId}/view?usp=sharing"

def insert_file(service, title, parent_id, mime_type, filename):
    media = MediaFileUpload(filename, mimetype=mime_type, resumable=True)
    media.stream()
    file_metadata = {
        'name': title
    }
    # Set the parent folder.
    if parent_id:
        file_metadata['parents'] = [parent_id]

    try:
        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id')
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")
        
        # Uncomment the following line to print the File ID
        print(f"File ID: {response.get('id')}")
        fileLink = get_file_link(response.get('id'))
        broadcast_to_enrolled_users('샤순신 강의배달!',f'링크: {fileLink}')

        return response
    except errors.HttpError as error:
        print(f'An error occured: {error}')
        return None

if __name__ == '__main__':
    savdAndBroadcastEmail('test.mpeg', f'{VIDEO_DIR}/1631065306.mpeg')
