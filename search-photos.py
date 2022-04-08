import json
import boto3
import time
import requests
import logging
import os


def getSlots(intent_request, context):

    search = intent_request['sessionState']['intent']['slots']['keyword1']['value']['interpretedValue']
    if intent_request['sessionState']['intent']['slots']['keyword2'] is None:
        search1 = "None"
    else:
        search1 = intent_request['sessionState']['intent']['slots']['keyword2']['value']['interpretedValue']
    keywords = [search, search1]

    return keywords


def getPhotoResults(keywords):
    endpoint = 'https://search-photos-najvtskrbxogitnfctvxaq2dia.us-east-1.es.amazonaws.com/photos/_search'
    headers = {'Content-Type': 'application/json'}
    prepared_q = []
    for k in keywords:
        prepared_q.append({"match": {"labels": k}})
    q = {"query": {"bool": {"should": prepared_q}}}
    r = requests.post(endpoint, auth=("ES-Demo2", "ES-Demo2"),
                      headers=headers, data=json.dumps(q))
    # print(r.text222)
    # r = {"took": 7, "timed_out": False, "_shards": {"total": 5, "successful": 5, "skipped": 0, "failed": 0}, "hits": {"total": {"value": 4, "relation": "eq"}, "max_score": 1.0, "hits": [{"_index": "photos", "_type": "photo", "_id": "5uWzhW4B9mNrwci-n6la", "_score": 1.0, "_source": {"objectKey": "uploaded_photos/gettyimages-91495990-170667a.jpg", "bucket": "photosb2", "createdTimestamp": "20191119-220611", "labels": ["Plant", "Tree", "Person", "Human", "Tree Trunk", "Outdoors"]}}, {"_index": "photos", "_type": "photo", "_id": "6OW5hW4B9mNrwci-Yqk8", "_score": 1.0, "_source": {"objectKey": "uploaded_photos/scott-eastwood.jpg", "bucket": "photosb2", "createdTimestamp": "20191119-221229", "labels": ["Person", "Human", "Canine", "Dog", "Pet", "Animal", "Mammal"]}}, {"_index": "photos", "_type": "photo", "_id": "5-W0hW4B9mNrwci-ZqlW", "_score": 1.0, "_source": {"objectKey": "uploaded_photos/pjimage-43-2.jpg", "bucket": "photosb2", "createdTimestamp": "20191119-220702", "labels": ["Tree", "Christmas Tree", "Ornament", "Plant", "Human", "Person"]}}, {"_index": "photos", "_type": "photo", "_id": "5eWzhW4B9mNrwci-V6mF", "_score": 1.0, "_source": {"objectKey": "uploaded_photos/pjimage-43-2.jpg", "bucket": "photosb2", "createdTimestamp": "20191119-220553", "labels": ["Tree", "Ornament", "Christmas Tree", "Plant", "Person", "Human"]}}]}}

    image_array = []
    for each in r.json()['hits']['hits']:
        objectKey = each['_source']['objectKey']
        bucket = each['_source']['bucket']
        image_url = "https://" + bucket + ".s3.amazonaws.com/" + objectKey
        image_array.append(image_url)
        print(each['_source']['labels'])
    print(image_array)
    return image_array


def dispatch(intent_request, context):
    """
    Called when the user specifies an intent for this bot.
    """

    # logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['sessionState']['intent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'SearchIntent':
        keywords = getSlots(intent_request, context)
        print(keywords)
        getPhotoResults(keywords)
        response = {'messages': [
            {'contentType': 'PlainText',
             'content': 'Here are the search results...'}
        ], 'sessionState': {
            'dialogAction': {
                'type': "Close"
            },
            'intent': {
                'slots': intent_request['sessionState']['intent']['slots'],
                'name': intent_request['sessionState']['intent']['name'],
                'state': "Fulfilled"
            }
        }}
    return response

    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    # logger.debug('event.bot.name={}'.format(event['bot']['name']))
    print(event)
    return dispatch(event, context)
