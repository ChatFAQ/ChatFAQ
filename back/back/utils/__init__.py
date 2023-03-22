import sys
import tempfile
from enum import Enum
from logging import getLogger

import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.forms import widgets

logger = getLogger(__name__)


class ToTempFile(object):
    """
    This helper is used on this project mainly for storing the certificate which are
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


class WSStatusCodes(Enum):
    _continue = 100
    switching_protocols = 101
    processing = 102
    early_hints = 103
    ok = 200
    created = 201
    accepted = 202
    non_authoritative_information = 203
    no_content = 204
    reset_content = 205
    partial_content = 206
    multi_status = 207
    already_reported = 208
    im_used = 226
    multiple_choices = 300
    moved_permanently = 301
    found_previously_moved_temporarily = 302
    see_other = 303
    not_modified = 304
    use_proxy = 305
    switch_proxy = 306
    temporary_redirect = 307
    permanent_redirect = 308
    bad_request = 400
    unauthorized = 401
    payment_required = 402
    forbidden = 403
    not_found = 404
    method_not_allowed = 405
    not_acceptable = 406
    proxy_authentication_required = 407
    request_timeout = 408
    conflict = 409
    gone = 410
    length_required = 411
    precondition_failed = 412
    payload_too_large = 413
    uri_too_long = 414
    unsupported_media_type = 415
    range_not_satisfiable = 416
    expectation_failed = 417
    i_am_a_teapot = 418
    misdirected_request = 421
    unprocessable_entity = 422
    locked = 423
    failed_dependency = 424
    too_early = 425
    upgrade_required = 426
    precondition_required = 428
    too_many_requests = 429
    request_header_fields_too_large = 431
    unavailable_for_legal_reasons = 451
    internal_server_error = 500
    not_implemented = 501
    bad_gateway = 502
    service_unavailable = 503
    gateway_timeout = 504
    http_version_not_supported = 505
    variant_also_negotiates = 506
    insufficient_storage = 507
    loop_detected = 508
    not_extended = 510
    network_authentication_required = 511

    @staticmethod
    def is_ok(status) -> bool:
        return status < 400


def is_migrating():
    return "makemigrations" in sys.argv or "migrate" in sys.argv


class PrettyJSONWidget(widgets.Textarea):
    def format_value(self, value):
        try:
            value = json.dumps(json.loads(value), indent=4, sort_keys=True)
            # these lines will try to adjust size of TextArea to fit to content
            row_lengths = [len(r) for r in value.split("\n")]
            self.attrs["rows"] = min(max(len(row_lengths) + 2, 10), 30)
            self.attrs["cols"] = min(max(max(row_lengths) + 2, 40), 120)
            return value
        except Exception as e:
            logger.warning("Error while formatting JSON: {}".format(e))
            return super(PrettyJSONWidget, self).format_value(value)
