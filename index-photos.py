import json
import boto3
import urllib.parse
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import inflection
import base64
s3 = boto3.client('s3')
REGION = 'us-east-1'
HOST = 'search-photos-5zhamvmcx654nihxkh6w4osoqa.us-east-1.es.amazonaws.com'
INDEX = 'photos'

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    print(event)

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    file_name = event['Records'][0]['s3']['object']['key']
    try:
        response = s3.head_object(Bucket=bucket, Key=key)
        print('response: ', response)
        print("CONTENT TYPE: " + response['ContentType'])
        photo = file_name
        bucket = bucket
        time = event['Records'][0]['eventTime']
        labels = detect_labels(photo, bucket)
        if 'x-amz-meta-customlabels' in response['ResponseMetadata']['HTTPHeaders']:
            customLabels = response['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels']
            customLabels = customLabels.split(',')
            labels.extend(customLabels)
        
        print(labels)
        for i in range(len(labels)):
            labels[i] = inflection.singularize(labels[i])
            
        re = index_document(photo, bucket, time, labels)
        print(re)

        return response['ContentType']
    
    except Exception as e:
        print(e)
        raise e

def detect_labels(photo, bucket):
     client = boto3.client('rekognition')
     response = client.detect_labels(Image={"S3Object": {"Bucket": bucket,"Name": photo}}, MaxLabels=3)
     labels = []
     print('Detected labels for ' + photo)
     for label in response['Labels']:
         #print(label)
         #print("Label: " + label['Name'])
         labels.append(label['Name'])
         #print("Confidence: " + str(label['Confidence']))


     return labels

def create_index():
    client = OpenSearch(hosts=[{
                                    'host': HOST,
                                    'port': 443
                                }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)
                        
    index_name = 'photos-index'
    index_body = {
      'settings': {
        'index': {
          'number_of_shards': 1
        }
      }
    }
    response = client.indices.create(index_name, body=index_body)
    return response

def index_document(photo, bucket, time, labels):
    client = OpenSearch(hosts=[{
                                    'host': HOST,
                                    'port': 443
                                }],
                        http_auth=get_awsauth(REGION, 'es'),
                        use_ssl=True,
                        verify_certs=True,
                        connection_class=RequestsHttpConnection)
                        
    document = {
        "objectKey": photo,
        "bucket": bucket, 
        "createdTimestamp": time, 
        "labels": labels}
    
    response = client.index(
        index = 'photos',
        body = document,
        id = photo,
        refresh = True
    )
    
    return response

def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
                    cred.secret_key,
                    region,
                    service,
                    session_token=cred.token)

