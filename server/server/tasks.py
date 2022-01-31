from __future__ import absolute_import
from celery import shared_task
from django.conf import settings

import requests
import datetime


@shared_task
def run_code(pipeline_id):
    r = requests.get(f'https://parsagon.io/api/pipelines/{pipeline_id}/code/')
    code = r.json()['code']
    start_time = datetime.datetime.now()
    try:
        exec(code)
    except Exception as e:
        requests.patch(f'https://parsagon.io/api/pipelines/{pipeline_id}/runs/', )
