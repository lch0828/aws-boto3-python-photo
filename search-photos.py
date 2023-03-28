from datetime import datetime, date
import boto3
from botocore.exceptions import ClientError
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import inflection
import json
SLOTS = ['query_term1', 'query_term2']
REGION = 'us-east-1'
HOST = 'search-photos-5zhamvmcx654nihxkh6w4osoqa.us-east-1.es.amazonaws.com'
INDEX = 'photos'
client = boto3.client('lexv2-runtime')

def lambda_handler(event, context):
    print('event:', event)
    msg_from_user = event['queryStringParameters']['q']
    print(msg_from_user)

    response = client.recognize_text(
            botId='WS3JRIDEYW', # MODIFY HERE
            botAliasId='H1JO8ULWZM', # MODIFY HERE
            localeId='en_US',
            sessionId='testuser',
            text=msg_from_user)
            
    print(response)
    slots = response['sessionState']['intent']['slots']
    
    labels = []
    for key in SLOTS:
        if slots[key] != None :
            labels.append(inflection.singularize(slots[key]['value']['resolvedValues'][0]))
            
    results = query(labels)
    print('query: ', results)
    urls = []
    
    for q in results:
        urls.append(boto3.client('s3').generate_presigned_url(ClientMethod='get_object', Params={'Bucket': 'spring-2023-cloud-hw2', 'Key': q},ExpiresIn=3600))
        
    print(urls)

    return {"isBase64Encoded": False,"statusCode": 200,'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        },"body": json.dumps({'results': urls})}
    

def query(term):
    query_string = ''
    for string in term:
        query_string += string + ' '
    q = {'size': 3, 'query': {'multi_match': {'query': query_string, 'fields': ['labels']}}}
    client = OpenSearch(hosts=[{
        'host': HOST,
        'port': 443
    }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)
    res = client.search(index=INDEX, body=q)
    print(res)
    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_id'])
    return results

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)
        
    
