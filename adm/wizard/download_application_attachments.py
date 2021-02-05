# -*- coding: utf-8 -*-+

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64, io
from datetime import date


class DownloadApplicationAttachments(models.TransientModel):
    _name = 'download.application.attachments'
    _description = "Download Application attachments"

    application_ids = fields.Many2many('adm.application')
    file_compressed_ids = fields.Many2many('ir.attachment')

    @api.model
    def _create_attachments_zip(self, attachment_ids, zip_bin):
        import zipfile
        # function to convert binary data

        def is_base64_decodestring(binary):
            try:
                return base64.decodebytes(binary)
            except Exception as e:
                raise ValidationError('Error: %s' % str(e))

        # 'attachments_%s.zip' % (''.join(map(str, attachment_ids.ids)))
        with zipfile.ZipFile(zip_bin, 'a') as attachment_zipfile:

            for attachment_id in attachment_ids:
                data = attachment_id.datas
                attachment_zipfile.writestr(attachment_id.name, is_base64_decodestring(data))

        # return attachment_zipfile

    def download_attachments(self):
        self.ensure_one()
        self.file_compressed_ids = False

        for application_id in self.application_ids:
            attachment_ids = application_id.attachment_ids
            with io.BytesIO() as zip_bin:
                self._create_attachments_zip(attachment_ids, zip_bin)
                base64_encoded_file = base64.b64encode(zip_bin.getvalue())
                attachment_name = '%s.zip' % application_id.name
                attachment_zip_id = self.env['ir.attachment'].sudo().create({
                    'name': attachment_name,
                    'datas': base64_encoded_file,
                    'mimetype': 'application/zip',
                    'type': 'binary',
                    })
                self.file_compressed_ids = self.file_compressed_ids + attachment_zip_id

        # Zip of files ;)
        with io.BytesIO() as zip_of_zip_bin:
            self._create_attachments_zip(self.file_compressed_ids, zip_of_zip_bin)
            base64_encoded_file = base64.b64encode(zip_of_zip_bin.getvalue())
            attachment_name = 'application_attachments_%s.zip' % date.today().strftime('%Y%m%d')
            zip_of_zip_attachment_id = self.env['ir.attachment'].sudo().create({
                'name': attachment_name,
                'datas': base64_encoded_file,
                'mimetype': 'application/zip',
                'type': 'binary',
                'public': True
                })

        return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/%s/%s' % (zip_of_zip_attachment_id.id, attachment_name),
            'target': 'self',
            }
