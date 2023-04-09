"""
This module provides an api to upload video 
on the authenticated user's youtube channel
"""
from googleapiclient import errors
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from google_cred import get_cred


def save(title, filepath):
    cred = get_cred()
    if cred is None:
        return None
    youtube = build('youtube', 'v3', credentials=cred, cache_discovery=False)
    media = MediaFileUpload(filepath, mimetype='video/mpeg', resumable=True)
    media.stream()

    body = dict(
        snippet=dict(
            title=title,
            description='스타강좌',
            tags=['Starcraft', 'Terran', 'Lecture']
        ),
        status=dict(
            privacyStatus="private"
        )
    )

    try:
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")

        print(f'upload done: {response}')
        print(f"File ID: {response.get('id')}")
        file_link = get_file_link(response.get('id'))
        print(file_link)

        return file_link
    except errors.HttpError as error:
        print(f'An error occured: {error}')
        return None


def get_file_link(file_id):
    return f"https://www.youtube.com/watch?v={file_id}"
