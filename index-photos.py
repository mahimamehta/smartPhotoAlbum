import json
import urllib.parse
import boto3
import requests

print('Loading function')

s3 = boto3.client('s3')


def detect_labels(photo, bucket):

    client = boto3.client('rekognition')

    response = client.detect_labels(Image={'S3Object': {'Bucket': bucket, 'Name': photo}},
                                    MaxLabels=10)

    print('Detected labels for ' + photo)
    print()
    labels = []
    for label in response['Labels']:
        labels.append(label['Name'])
    return labels


def storeToES(index, json):
    host = 'https://search-photos-najvtskrbxogitnfctvxaq2dia.us-east-1.es.amazonaws.com/'
    path = 'photos/_doc/'
    url = host + path
    headers = {'Content-Type': 'application/json'}
    r = requests.post(url, auth=("ES-Demo2", "ES-Demo2"),
                      data=json, headers=headers)
    # print(r.text)


def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))

    buckets = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(
        event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    labels = detect_labels(key, buckets)
    print(key)
    print(s3.head_object(Bucket=buckets, Key=key))
    timestamp = event['Records'][0]['eventTime']
    jsonObj = {
        "objectKey": key,
        "bucket": buckets,
        "createdTimestamp": timestamp,
        "labels": labels
    }
    print("---------")
    print(jsonObj)
    storeToES('photos', json.dumps(jsonObj))
    try:
        response = s3.get_object(Bucket=buckets, Key=key)
        print("CONTENT TYPE: " + response['ContentType'])
        return response['ContentType']
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, buckets))
        raise e
