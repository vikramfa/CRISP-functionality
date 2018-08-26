from rest_services.models import Batch
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from rest_services.api.service.excelCreationService import ExcelCreationService
from django.conf import settings

class WebhookProcessService:

    def persistWebhooksStatusInfo(self, dictWebHooks):
        output_rec_cnt = int(dictWebHooks['Record Count']) #output record count
        batchId = dictWebHooks['Batch ID']
        batchName = dictWebHooks['batch_api']
        batchState = dictWebHooks['Status']

        try:
            batch_obj = Batch.objects.get(pk=batchId)
        except Batch.DoesNotExist:
            print("Batch Record Not Found, id:", batchId)
            return
        input_rec_cnt = batch_obj.total_ips
        batch_obj.batch_status = batchState
        if(batchState == 'Completed'):

            if(batchName == 'shodan'):
                batch_obj.shodan_input_records = input_rec_cnt
                batch_obj.shodan_processed_records = output_rec_cnt
                batch_obj.shodan_failed_records = abs(input_rec_cnt - output_rec_cnt)
                batch_obj.shodan_records_update = 'Y'
            elif(batchName == 'domainiq'):
                batch_obj.domainiq_input_records = input_rec_cnt
                batch_obj.domainiq_processed_records = output_rec_cnt
                batch_obj.domainiq_failed_records = abs(input_rec_cnt - output_rec_cnt)
                batch_obj.domainiq_records_update = 'Y'
            elif(batchName == 'censys'):
                batch_obj.censys_input_records = input_rec_cnt
                batch_obj.censys_processed_records = output_rec_cnt
                batch_obj.censys_failed_records = abs(input_rec_cnt - output_rec_cnt)
                batch_obj.censys_records_update = 'Y'
        batch_obj.save()

        if (batchState == 'Completed'):

            result_file_name = '%s/result_files/batch_%s.xlsx' % (settings.MEDIA_ROOT, batch_obj.batch_id)
            if(batch_obj.shodan_records_update == 'Y' and batch_obj.domainiq_records_update == 'Y' and
            batch_obj.censys_records_update == 'Y' and batch_obj.shodan_processed_records>0 and
            batch_obj.domainiq_processed_records>0 and batch_obj.censys_processed_records>0 and
            not default_storage.exists(result_file_name)):


                while True:

                    if(default_storage.exists('%s/result_files/batch_%s_%s.json' % (settings.MEDIA_ROOT, batch_obj.batch_id, 'shodan')) and
                    default_storage.exists('%s/result_files/batch_%s_%s.json' % (settings.MEDIA_ROOT, batch_obj.batch_id, 'censys')) and
                    default_storage.exists('%s/result_files/batch_%s_%s.json' % (settings.MEDIA_ROOT, batch_obj.batch_id, 'domainiq')) and
                    not default_storage.exists(result_file_name)):
                        xlsService = ExcelCreationService()
                        xlsService.createFinalXlsFile(result_file_name, batch_obj)
                        break
        print('result file successfully generated, result file name:',result_file_name)