from django.core.exceptions import ValidationError
from django.db import models
import os
import mimetypes

allowed_mimetypes = ('text/csv','application/vnd.ms-excel','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','text/tab-separated-values')


def validate_files(value):
    try:
        file_size= value.size
        if file_size > os.getenv('FILE_UPLOAD_MAX_MEMORY_SIZE',2500000):
            raise ValidationError("The maximum file size that can be uploaded is 2.5MB")
        else:
            mime_message = ("MIME type '%(mimetype)s' is not valid. Allowed types are: %(allowed_mimetypes)s.")
            # extension = os.path.splitext(str(value))[1]
            mimetype = mimetypes.guess_type(value.name)[0]
            if not (mimetype in allowed_mimetypes):
                message = mime_message % {
                    'mimetype': mimetype,
                    'allowed_mimetypes': ', '.join(allowed_mimetypes)
                }
                raise ValidationError(message)
            else:
                return value
    except IOError:
        raise ValidationError("No Batch file given")

