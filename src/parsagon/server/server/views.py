from rest_framework.decorators import api_view
from rest_framework.response import Response
from server.tasks import run_code

import subprocess
import pandas as pd
from pyvirtualdisplay import Display
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from lxml import etree
import lxml.html
import time


@api_view(['GET'])
def ping(request):
    return Response('pong')


@api_view(['POST'])
def update(request):
    subprocess.run(["/home/ubuntu/parsagon/parsagon-local-server/bin/parsagon-server-update"])
    return Response('OK')


@api_view(['POST'])
def read_db(request):
    db_type = request.data['db_type']
    db_name = request.data['db_name']
    user = request.data['db_user']
    password = request.data['db_password']
    host = request.data['db_host']
    port = request.data['db_port']
    table = request.data['table']
    schema = request.data['schema']

    con = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'

    df_iter = pd.read_sql_table(table, con=con, schema=schema, chunksize=100)
    df = next(df_iter)
    result = df.to_dict(orient='records')

    return Response(result)


@api_view(['POST'])
def write_db(request):
    db_type = request.data['db_type']
    db_name = request.data['db_name']
    user = request.data['db_user']
    password = request.data['db_password']
    host = request.data['db_host']
    port = request.data['db_port']
    table = request.data['table']
    schema = request.data['schema']

    con = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'

    return Response('OK')


@api_view(['POST'])
def fetch_web(request):
    url = request.data['url']
    actions = request.data['actions']
    options = {'disable_capture': True}
    display = Display(visible=False, size=(1680, 1050)).start()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), seleniumwire_options=options)
    driver.maximize_window()
    driver.get(url)
    time.sleep(2)
    for action in actions:
        pass
    page_source = driver.page_source
    driver.quit()
    display.stop()
    parser = lxml.html.HTMLParser(remove_comments=True, remove_pis=True)
    root = lxml.html.fromstring(page_source, parser=parser)
    etree.strip_elements(root, 'script', with_tail=False)
    etree.strip_elements(root, 'noscript', with_tail=False)
    root.make_links_absolute(url)
    return Response({'url': url, 'actions': actions, 'html': lxml.html.tostring(root)})


@api_view(['POST'])
def run_pipeline(request):
    run_code.delay(request.data['pipeline_id'], request.data['run_id'])
    return Response('OK')
