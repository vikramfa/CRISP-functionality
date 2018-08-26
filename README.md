# cyber-batch-job
  
- This Batch API is built on python version 3.6.4 and Django Rest Framework which provides restful microservices to upload the file in Docker mount Volume and pusblishes the message in KAFKA Server. 
- It persists the data in postgres.
- Generates the result excel file from the partial ".json" files of Shodan, Censys and DomainIQ. 

## Documentation

Swagger docs of this API at the path `http://localhost:8000/api-docs`.


## Requirements 
* python==3.6.4
* djangorestframework==3.8.2
* Postgres 10
* Kafka-python

## Setup 
There are 2 setup methods. **Please choose one only.**
1. Development (if you are actually developing this project)
2. Operation via Docker (if you just want to run this project)

### Development option:

#### KAFKA Configuration:

We need to bring up the KAFKA Docker Container first. Follow the Readme file of Kafka and create a topic name "batch".

Things to be noted during Kafka configurations:
- In docker-compose.yml file of Kafka, make sure the below line has value 'kafkaserver':
ADVERTISED_HOST: kafkaserver

- Make sure to add below line in hosts file of your local machine.
127.0.0.1 kafkaserver

As mentioned in the Readme of KAFKA, just open the consumer console by following command from local machine(kafka\kafka_2.11-1.1.0\bin\windows).
- kafka-console-consumer.bat --bootstrap-server localhost:9092 --topic batch --from-beginning

To check the messages are getting published.

#### To Run API

python manage.py migrate
python manage.py runserver

### Operation via Docker

Prerequisites:

For Unix-based systems: You would need to set the "wait-for-it.sh" bash script to executable, because the script is set to non-executable by default with Git.
```
sudo chmod a+x ./wait-for-it.sh
```
For Windows: Unfortunately due to the lack of unix permissions, you would have to amend the "wait-for-it.sh" bash script permissions within the running container after you have `docker-compose up -d`. And you probably have to do this everytime you destroy and bring up the `web` container.
```
docker-compose run web bash
chmod +x ./wait-for-it.sh
exit
```

And now run following commands in the command prompt from the directory where docker-compose.yml resides.
- docker-compose up -d
- docker-compose run web python manage.py migrate
After this command, we can see the containers up and running.

## REST API URL 

- Create Batch API (POST): localhost:8000/api/batches/
- Retrieve Batch (GET): localhost:8000/api/batches/{batchid}
- List Batches (GET): localhost:8000/api/batches/
- Cancel Batch (POST): localhost:8000/api/batches/{batchid}/cancel/


### Filtering Urls:
- localhost:8000/api/batches?batch_status=DONE (possible values = DONE,INIT,CANCELLED,FAILED)

### Streamsets Pipeline Status Information to Kafka Topic:
- KAFKA Topic Name: status
- KAFKA status data format : { "Batch ID":24,"Record Count":3,"Status":"Completed","batch_api":"domainiq/censys/shodan" }

Status information of the streamsets pipeline will be consumed from KAFKA topic by cyber-batch-job API.
The failed/processed information will be updated in BATCH table.
Post Updation, the final Batch XLS file will be triggered.

To run unit test case:
- docker-compose run web python manage.py test  (Runs all the tests.py)
- docker-compose run web python manage.py test rest_services ( Runs the test cases under rest_services)


## Testing 
To run unit test case:
- docker-compose run web python manage.py test  (Runs all the tests.py)
- docker-compose run web python manage.py test rest_services ( Runs the test cases under rest_services)

## Road Map (Optional)
N/A

## Discussion (Optional)
N/A

## Maintained by 

| Owner Contact | Details | 
| ------------- | :----- |
|Name | Vigneshwar.S|
|Title | Consultant|
|Email| vigsrinivasan@deloitte.com|


## Links for reference
The Python Tutorial: [Tutorial on Python](https://docs.python.org/3/tutorial/) 




