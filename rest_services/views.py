from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework import status
from .api.serializers import BatchSerializer,EmployeeSerializer
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from .models import Batch,Employee
from django.conf import settings
from rest_framework.renderers import JSONRenderer
from rest_framework import viewsets, schemas
from rest_framework.decorators import action
from rest_framework import mixins
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import datetime
import os, re
from django.http import HttpResponse
from .authentication import ApiAuthentication
from .permissions import IsAuthenticated

producer = KafkaProducer(
    bootstrap_servers=settings.KAFKA_SERVER,
    retries=5
)

class BatchViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        Return a list of all Batches in the system.
    """
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer
    filter_fields = ('batch_status', 'user_created_by')
    parser_classes = ( MultiPartParser, FormParser)
    authentication_classes = (ApiAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(manual_parameters =[openapi.Parameter('Authorization', openapi.IN_HEADER, "JWT ", required=True, type=openapi.TYPE_STRING)], responses={201: 'Created'})
    def create(self, request, *args, **kwargs):
        """
            Create a Batch in the system, uploads the file and publish the message in Kafka Server.
        """
        user_created_by = request.user['id']
        file_serializer = BatchSerializer(data=request.data)
        if file_serializer.is_valid():
            file = request.FILES['source_file_name']
            file_content_dict = file.get_dict()
            # Removing duplicate ip values and empty values before publishing to Kafka.

            #Checking whether key is present in dict
            if not len(file_content_dict.keys()) == 0:
                key = list(file_content_dict.keys())[0]

                #Checking that key is not empty string
                if not len(key.strip()) == 0:
                    value = file_content_dict[key]

                    #Assigning to set, to remove duplicate ip strings
                    ip_sets = set(value)

                    # Removing empty strings
                    ip_list = [str(ip) for ip in ip_sets if len(str(ip).strip()) != 0]

                    file_content_dict[key] = ip_list
                    total_ips = len(ip_list)

                    if total_ips != 0:
                        for ip in ip_list:

                            match = re.match('(([2][5][0-5]\.)|([2][0-4][0-9]\.)|([0-1]?[0-9]?[0-9]\.)){3}(([2][5][0-5])|([2][0-4][0-9])|([0-1]?[0-9]?[0-9]))', ip)
                            if not match:
                                batch = file_serializer.save(user_created_by=user_created_by, batch_status='FAILED')
                                return Response("The file contains Invalid Ip Address", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
                            else:
                                continue

                        batch = file_serializer.save(user_created_by=user_created_by, total_ips=total_ips, shodan_records_update='N', domainiq_records_update='N', censys_records_update='N')
                        batch_id_dict = { "batch_id": file_serializer.data['batch_id'], "action": "create" }
                        file_content_dict.update(batch_id_dict)
                        json_form_val = JSONRenderer().render(file_content_dict)
                        kafka_topic = 'batch'

                        producer.send(kafka_topic, json_form_val)
                        producer.flush()
                        return Response(file_serializer.data, status=status.HTTP_201_CREATED)

                    else:
                        return Response("The file contains no Ip Address", status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            return Response(file_serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    def retrieve(self, request, pk):
        """
         Retrieves a Batch record that matches the given batch_id.
        """
        try:
            batch_obj = Batch.objects.get(pk=pk)
        except Batch.DoesNotExist:
            return Response('Batch Record Not Found', status=status.HTTP_404_NOT_FOUND)
        serializer = BatchSerializer(batch_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(manual_parameters =[openapi.Parameter('batch_id', openapi.IN_PATH, "batch id", required=True, type=openapi.TYPE_INTEGER ),
                                             openapi.Parameter('batch_name', openapi.IN_FORM, "", required=False, type=openapi.TYPE_STRING ),
                                             openapi.Parameter('source_file_name', openapi.IN_FORM, "", required=False, type=openapi.TYPE_FILE ),
                                             openapi.Parameter('file_format', openapi.IN_FORM, "", required=False, type=openapi.TYPE_STRING )
                                             ], responses={ 200: 'OK' })
    @action(methods=['post'], detail=True)
    def cancel(self, request, pk=None):
        """
        Updates the batch status to cancel.
        """
        try:
            batch_obj = Batch.objects.get(pk=pk)
        except Batch.DoesNotExist:
            return Response('Batch Record Not Found', status=status.HTTP_404_NOT_FOUND)

        batch_obj.batch_status = "CANCELLED"
        batch_obj.cancelled_at = datetime.datetime.now()
        batch_obj.save()

        cancel_dict = {"batch_id": pk, "action": "cancel"}
        json_val = JSONRenderer().render(cancel_dict)
        kafka_topic = 'batch'

        producer.send(kafka_topic, json_val)
        producer.flush()

        serializer = BatchSerializer(batch_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)



    @swagger_auto_schema(manual_parameters =[openapi.Parameter('batch_id', openapi.IN_PATH, "batch id", required=True, type=openapi.TYPE_INTEGER),
                                             ], responses={200: 'OK'})
    @action(methods=['get'], detail=True)
    def download_result(self, request, pk=None):
        """
        Download the final batch xls file which was uploaded on the system based on the batch_id
        """
        # Assuming that result file will have the prefix 'batch_' followed by batch_id,
        # thereby filtering the corresponding result file by batch_id from the path of the url
        file_name = 'batch_%s.xlsx' % pk
        file_path = os.path.join(settings.MEDIA_ROOT, 'result_files', file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
        return Response('File Not Found', status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('batch_id', openapi.IN_PATH, "batch id", required=True, type=openapi.TYPE_INTEGER),
        ], responses={200: 'OK'})
    @action(methods=['get'], detail=True)
    def download_source(self, request, pk=None):
        """
        Download the source file which was uploaded on the system based on the batch_id
        """
        # Assuming that source file will be stored in the batch_files directoryhave the prefix 'batch_' followed by batch_id,
        # thereby filtering the corresponding source file by fetching the
        # file name from Batch Table with batch_id from the the path of the url
        file_name = 'source%s.xlsx' % pk
        try:
            batch_obj = Batch.objects.get(pk=pk)
        except Batch.DoesNotExist:
            return Response('Batch Record Not Found', status=status.HTTP_404_NOT_FOUND)
        file_path = os.path.join(settings.MEDIA_ROOT, 'batch_files', batch_obj.source_file_name.name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
        return Response('File Not Found', status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(manual_parameters =[openapi.Parameter('batch_id', openapi.IN_PATH, "batch id", required=True, type=openapi.TYPE_INTEGER),
                                             ], responses={200: 'OK'})
    @action(methods=['get'], detail=True)
    def download_error(self, request, pk=None):
        """
        Download the error file which was uploaded on the system based on the batch_id
        """
        # Assuming that result file will have the prefix 'error_' followed by batch_id,
        # thereby filtering the corresponding result file by batch_id from the path of the url
        file_name = 'error_%s.xlsx' % pk
        file_path = os.path.join(settings.MEDIA_ROOT, 'error_files', file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
        return Response('File Not Found', status=status.HTTP_404_NOT_FOUND)

class StudentViewSet(mixins.CreateModelMixin,viewsets.GenericViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def create(self, request, *args, **kwargs):
        print(request.data)
        student_serializer = EmployeeSerializer(data = request.data)
        if student_serializer.is_valid(raise_exception=ValueError):
            print('serializer',student_serializer.validated_data)
            student_serializer.create(validated_data=request.data)
            return Response(student_serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(student_serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
