# Pick random file and encode it ready to be attached to email

import logging
import os
import random

import mimetypes

from email import encoders
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText


class PickRandomFile(object):

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.base_fake_files_dir = "Fake_Files/"

    def pick_rand_file_path(self):
        # self.logger.debug("Parent Dir: %s" % str(os.pardir))
        self.logger.debug("Current Working Dir: %s" % str(os.getcwd()))
        grand_par_dir = os.path.realpath(os.path.join(os.getcwd(), os.pardir))
        self.logger.debug("Get Current Grand Parent Directory: %s" % grand_par_dir)
        fake_files_dir = os.path.join(grand_par_dir, self.base_fake_files_dir)
        self.logger.debug("Fake files dir: %s" % fake_files_dir)

        # Get all file names (also returns directory names :-(  )
        file_names_list = os.listdir(fake_files_dir)
        random_f_name = random.choice(file_names_list)

        return os.path.join(fake_files_dir, random_f_name)

    def pick_random_file_and_make_mime(self):
        random_file_path = self.pick_rand_file_path()
        # file_name = random_file_path.split("/")
        file_name = random_file_path.rpartition("/")[2]
        self.logger.debug("Random File Path: %s" % random_file_path)

        # Copied from python documentation
        # Guess the content type based on the file's extension.  Encoding
        # will be ignored, although we should check for simple things like
        # gzip'd or compressed files.
        ctype, encoding = mimetypes.guess_type(random_file_path)
        if ctype is None or encoding is not None:
            # No guess could be made, or the file is encoded (compressed), so
            # use a generic bag-of-bits type.
            ctype = 'application/octet-stream'
        maintype, subtype = ctype.split('/', 1)
        if maintype == 'text':
            with open(random_file_path) as fp:
                # Note: we should handle calculating the charset
                mime_attachment_part = MIMEText(fp.read(), _subtype=subtype)
        elif maintype == 'image':
            with open(random_file_path, 'rb') as fp:
                mime_attachment_part = MIMEImage(fp.read(), _subtype=subtype)
        elif maintype == 'audio':
            with open(random_file_path, 'rb') as fp:
                mime_attachment_part = MIMEAudio(fp.read(), _subtype=subtype)
        else:
            with open(random_file_path, 'rb') as fp:
                mime_attachment_part = MIMEBase(maintype, subtype)
                mime_attachment_part.set_payload(fp.read())
            # Encode the payload using Base64
            encoders.encode_base64(mime_attachment_part)

        # Set the filename parameter
        mime_attachment_part.add_header('Content-Disposition', 'attachment', filename=file_name)
        # outer.attach(mime_attachment_part)

        return  mime_attachment_part



rand_picker = PickRandomFile()
rand_picker.pick_random_file_and_make_mime()

