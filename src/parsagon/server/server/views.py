from rest_framework.decorators import api_view
from rest_framework.response import Response
from server.tasks import run_code

import pandas as pd


@api_view(['GET'])
def ping(request):
    return Response('pong')


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
def run_pipeline(request):
    run_code.delay(request.data['pipeline_id'], request.data['run_id'])
    return Response('OK')
