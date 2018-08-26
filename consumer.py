#!/usr/bin/env python
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "batchapi.settings")
django.setup()

from django.conf import settings
# from confluent_kafka import Consumer, KafkaError
from kafka import KafkaConsumer
import json
from rest_services.api.service.webhooksProcessService import WebhookProcessService

def process_streamsets(topic, r_body):
    """
    Creates partial file with streamsets output.
    If streamsets output is complete, generate result file from combined data.
    :return:
    """
    # Extract batch id
    # expecting below json format from topic 'batch'
    #{"batch_id":1, "Batch Name":"crisp", "File Upload Time":"06-11-2018", "Number of Failed Records":0, "Number of Record Processed":1, "Number of Records with no data available":"N/A", "Record Processing Time":"1 minute", "Uploader Name":"rajsekar"}
    try:
        data = json.loads(r_body)
    except (ValueError, KeyError, TypeError):
        print ("Request body is not in JSON format")
        return
    if topic in ('shodan', 'censys', 'domainiq') and len(data) == 0:
        return
    batch_id = data[0]['batch_id']

    # Generate partial file
    file_name = '%s/result_files/batch_%s_%s.json' % (settings.MEDIA_ROOT, batch_id, topic)
    result_file_name = '%s/result_files/batch_%s.xlsx' % (settings.MEDIA_ROOT, batch_id)
    with open(file_name, 'w') as jsonfile:
        json.dump(data, jsonfile)
        jsonfile.close()

        #batch_completed_post_hook()

#def batch_completed_post_hook():
    # send push notification, send email notification

def process_streamsets_audit_details(topic, r_body):
    """
    process the audit details from the kafka topic 'status' as a streamsets output.
    updated it in Batch Table, generate final batch result file from combined data.
    :return:
    """
    # Extract batch id
    # expecting below json format from topic 'status' for audit details of pipeline
    #{ "Batch ID": 24, "Record Count": 3, "Status": "Completed","batch_api": "domainiq" }

    try:
        data = json.loads(r_body)
    except (ValueError, KeyError, TypeError):
        print("Request body is not in JSON format")
        return
    if topic in ('status') and len(data) == 0:
        return

    webhookService = WebhookProcessService()
    webhookService.persistWebhooksStatusInfo(data)

if __name__ == '__main__':
    # Use the KafkaConsumer class to consume latest messages and auto-commit offsets
    # `consumer_timeout_ms` param is used in order to stop iterating KafkaConsumer
    # if no message can be found after 1sec
    # consumer = Consumer({
    #     'bootstrap.servers': settings.KAFKA_SERVER,
    #     'group.id': 'batch',
    #     'default.topic.config': {
    #         'auto.offset.reset': 'smallest'
    #     }
    # })
    # consumer.subscribe(['batch', 'shodan', 'censys', 'domainiq'])

    # while True:
    #     message = consumer.poll(1.0)

    #     if message is None:
    #         continue
    #     if message.error():
    #         if message.error().code() == KafkaError._PARTITION_EOF:
    #             continue
    #         else:
    #             print(message.error())
    #             break

    #     print('Received message: {}'.format(message.value().decode('utf-8')))

    #     topic = message.topic()
    #     request_body = message.value().decode('utf-8')
    #     print ("%s:%d:%d: value=%s" % (
    #         message.topic(), message.partition(),
    #         message.offset(), message.value().decode('utf-8'))
    #         )
    #     process_streamsets(topic, request_body)

    # consumer.close()

    consumer = KafkaConsumer(
        'shodan', 'censys', 'domainiq', 'status',
        bootstrap_servers=settings.KAFKA_SERVER,
        consumer_timeout_ms=1000
    )

    while True:
        for message in consumer:
            if message is not None:
                topic = message.topic
                request_body = message.value.decode('utf-8')
                print ("%s:%d:%d: value=%s" % (
                    message.topic, message.partition,
                    message.offset, request_body)
                    )
                if topic in ('shodan', 'censys', 'domainiq'):
                    process_streamsets(topic, request_body)
                elif topic == 'status':
                    process_streamsets_audit_details(topic, request_body)
    
    consumer.close()
