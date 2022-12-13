from django.core.files.uploadedfile import InMemoryUploadedFile
import requests
import tempfile


class ToTempFile(object):
    """
    this helper is used on this project mainly for storing the certificate which are
    in environment variables into temporary files which will immediately be
    deleted when finished its usage.

    There is a security problem, if the process crash before __exit__
    then we will have a dangling certificate in a system temp file
    """

    def __init__(self, value, download=False):
        self.value = value
        self.download = download

    def __enter__(self):
        self.file = tempfile.NamedTemporaryFile()
        self.file.__enter__()
        if self.download:
            res = requests.get(self.value)
            self.file.write(res.content)
        elif type(self.value) is InMemoryUploadedFile:
            for chunk in self.value.chunks():
                self.file.write(chunk)
        else:
            self.file.write(str.encode(self.value))
        self.file.seek(0)
        return self.file.name

    def __exit__(self, exc_type, exc_value, traceback):
        self.file.__exit__(exc_type, exc_value, traceback)
