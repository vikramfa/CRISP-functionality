from rest_services.models import Batch
from rest_services.models import Employee
from rest_services.models import EmployeeAddress
from rest_framework import serializers


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        read_only_fields = ('user_created_by','total_ips','batch_status','created_at','cancelled_at',)
        exclude = ()

# class ResultSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Batch
#         fields = ['batch_id','src_ip','batch_status','timestamp','user_created_by']




class EmployeeAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAddress
        fields = ('city',)


class EmployeeSerializer(serializers.ModelSerializer):
    stu_add = EmployeeAddressSerializer(required=True)
    #address = serializers.RelatedField(many=True,read_only=True)
    class Meta:
        model = Employee
        fields = ('name','marks','stu_add')

    def create(self, validated_data):
        """
        Overriding the default create method of the Model serializer.
        :param validated_data: data containing all the details of student
        :return: returns a successfully created student record
        """
        print('validated_data',validated_data)
        address_data = validated_data.pop('stu_add')
        address = EmployeeAddressSerializer.create(EmployeeAddressSerializer(), validated_data=address_data)
        print(type(address))
        employee, created = Employee.objects.update_or_create(stu_add=address,
                                                                name=validated_data.pop('name'),marks=validated_data.pop('marks'))
        return employee

