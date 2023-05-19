"""
This module provides an api to upload video 
on the authenticated user's youtube channel
"""
import asyncio
import http.client as httplib
import httplib2
from googleapiclient import errors
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_cred import get_cred
from logger_config import logger
from errors import VideoUploadFailure

httplib2.RETRIES = 1
MAX_RETRIES=3

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

async def resumable_upload(insert_request):
    """
    Start resumable upload using youtube api.
    """
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            status, response = await asyncio.to_thread(insert_request.next_chunk)
            if status:
                logger.info("Uploaded %d%%", int(status.progress() * 100))
        except errors.HttpError as exc:
            if exc.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred while uploading:\n%s" % (exc.resp.status,exc.content)
            else:
                logger.error('A nonretryable error occured while uploading: %s', exc)
                return None
        except RETRIABLE_EXCEPTIONS as exc:
            error = "A retriable error occurred: %s" % exc
        if error is not None:
            logger.error('Error while uploading: %s', error)
            retry += 1
            if retry > MAX_RETRIES:
                logger.error("Youtube uploader retry failed: Exceeded max retry count")
                raise VideoUploadFailure()
    if response is not None:
        if 'id' in response:
            logger.info('upload done: %s', response)
            logger.info("File ID: %s", response.get('id'))
            file_link = get_file_link(response.get('id'))
            logger.info('file link: %s', file_link)
            return file_link
    else:
        logger.error('File upload eventually failed.')
        return None


async def save(title, filepath):
    """
    Save video asynchronously
    """
    cred = await get_cred()
    if cred is None:
        return None
    youtube = build('youtube', 'v3', credentials=cred, cache_discovery=False)
    media = MediaFileUpload(filepath, mimetype='video/mpeg', resumable=True, chunksize=5*1024*1024)
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

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    try:
        return await resumable_upload(insert_request)
    except VideoUploadFailure as exc:
        logger.error("Stop uploading: %s", exc)
        return None
    except Exception as exc:
        logger.error("Retrying upload from the first: %s", exc)
        return await resumable_upload(insert_request)


def get_file_link(file_id):
    return f"https://www.youtube.com/watch?v={file_id}"
