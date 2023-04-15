import asyncio
from googleapiclient import errors
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from constants import VIDEO_DIR
from google_cred import get_cred


async def save(filename, filepath):
    cred = await get_cred()
    service = build('drive', 'v3', credentials=cred, cache_discovery=False)
    return await asyncio.to_thread(insert_file, service, filename, '1bE-A_oYEyRjsBJZrKGrgeNLNrzktwR87', 'video/mpeg', filepath)


def get_file_link(fileId):
    return f"https://drive.google.com/file/d/{fileId}/view?usp=sharing"


async def insert_file(service, title, parent_id, mime_type, filename):
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
        file_link = get_file_link(response.get('id'))
        return file_link
    except errors.HttpError as error:
        print(f'An error occured: {error}')
        return None


# if __name__ == '__main__':
#     save('test.mpeg', f'{VIDEO_DIR}/1631065306.mpeg') TODO: convert it to run async method
