import base64
import io
import json
import os.path as osp
import sqlite3

import PIL.Image

from labelme._version import __version__
from labelme.logger import logger
from labelme import PY2
from labelme import QT4
from labelme import utils

from labelme.utils.db import query, dict_to_json_blob

from ipdb import set_trace

class LabelFileError(Exception):
    pass


class LabelFile(object):

    suffix = '.json'

    def __init__(self, filename=None):
        self.db_id = None
        self.db_row = None

        self.shapes = ()
        self.imagePath = None
        self.imageData = None
        if filename is not None:
            self.load(filename)
        self.filename = filename

    @staticmethod
    def load_from_db(_id):

        logger.info('Loading LabelFile from DB id={}'.format(_id))

        _id = int(_id)

        # Fetch from DB
        # ----------------------------------------
        row = query("""
        SELECT
            id,
            created_at,
            updated_at,
            image_path,
            labels
        FROM labels
            WHERE id = ? LIMIT 1"""
            , (_id,))[0]

        lf = LabelFile()

        lf.db_id = _id
        lf.db_row = row

        # TODO: FIX: We may need the absolute path? Or relative to what?
        lf.imagePath = lf.db_row['image_path']
        lf.filename = osp.splitext(lf.imagePath)[0] + '.json'

        # Load shapes, etc. but from DB
        lf.load(lf.filename, True)

        return lf

    @staticmethod
    def load_image_file(filename):
        try:
            image_pil = PIL.Image.open(filename)
        except IOError:
            logger.error('Failed opening image file: {}'.format(filename))
            return

        # apply orientation to image according to exif
        image_pil = utils.apply_exif_orientation(image_pil)

        with io.BytesIO() as f:
            ext = osp.splitext(filename)[1].lower()
            if PY2 and QT4:
                format = 'PNG'
            elif ext in ['.jpg', '.jpeg']:
                format = 'JPEG'
            else:
                format = 'PNG'
            image_pil.save(f, format=format)
            f.seek(0)
            return f.read()

    def load(self, filename, from_db=False):
        keys = [
            'imageData',
            'imagePath',
            'lineColor',
            'fillColor',
            'shapes',  # polygonal annotations
            'flags',   # image level flags
            'imageHeight',
            'imageWidth',
        ]
        try:
            if from_db:
                data = json.loads(self.db_row['labels'])
            else:
                with open(filename, 'rb' if PY2 else 'r') as f:
                    data = json.load(f)

            if 'imageData' in data and data['imageData'] is not None:
                imageData = base64.b64decode(data['imageData'])
                if PY2 and QT4:
                    imageData = utils.img_data_to_png_data(imageData)
                imagePath = data['imagePath']
            else:

                # FIX: Relative paths
                if from_db:
                    imagePath = self.db_row['image_path']
                else:
                    # relative path from label file to relative path from cwd
                    imagePath = osp.join(osp.dirname(filename), data['imagePath'])
                imageData = self.load_image_file(imagePath)

            flags = data.get('flags') or {}

            self._check_image_height_and_width(
                base64.b64encode(imageData).decode('utf-8'),
                data.get('imageHeight'),
                data.get('imageWidth'),
            )
            lineColor = data['lineColor']
            fillColor = data['fillColor']
            shapes = (
                (
                    s['label'],
                    s['points'],
                    s['line_color'],
                    s['fill_color'],
                    s.get('shape_type', 'polygon'),
                    s.get('flags', {}),
                )
                for s in data['shapes']
            )

        except Exception as e:
            print(e)
            set_trace()
            raise LabelFileError(e)

        otherData = {}
        for key, value in data.items():
            if key not in keys:
                otherData[key] = value

        # Only replace data after everything is loaded.
        self.flags = flags
        self.shapes = shapes
        self.imagePath = imagePath
        self.imageData = imageData
        self.lineColor = lineColor
        self.fillColor = fillColor
        self.filename = filename
        self.otherData = otherData

    @staticmethod
    def _check_image_height_and_width(imageData, imageHeight, imageWidth):
        img_arr = utils.img_b64_to_arr(imageData)
        if imageHeight is not None and img_arr.shape[0] != imageHeight:
            logger.error(
                'imageHeight does not match with imageData or imagePath, '
                'so getting imageHeight from actual image.'
            )
            imageHeight = img_arr.shape[0]
        if imageWidth is not None and img_arr.shape[1] != imageWidth:
            logger.error(
                'imageWidth does not match with imageData or imagePath, '
                'so getting imageWidth from actual image.'
            )
            imageWidth = img_arr.shape[1]
        return imageHeight, imageWidth

    def save(
        self,
        filename,
        shapes,
        imagePath,
        imageHeight,
        imageWidth,
        imageData=None,
        lineColor=None,
        fillColor=None,
        otherData=None,
        flags=None,
        to_db=False,
    ):
        if imageData is not None:
            imageData = base64.b64encode(imageData).decode('utf-8')
            imageHeight, imageWidth = self._check_image_height_and_width(
                imageData, imageHeight, imageWidth
            )
        if otherData is None:
            otherData = {}
        if flags is None:
            flags = {}
        data = dict(
            version=__version__,
            flags=flags,
            shapes=shapes,
            lineColor=lineColor,
            fillColor=fillColor,
            imagePath=imagePath,
            imageData=imageData,
            imageHeight=imageHeight,
            imageWidth=imageWidth,
        )
        for key, value in otherData.items():
            data[key] = value
        try:
            if to_db:

                # Delete imageData since we are not saving the file in the db
                del data['imageData']

                rows = query("""
                UPDATE labels SET
                    labels = ?
                    WHERE
                    id = ?
                """, (dict_to_json_blob(data), self.db_id))

                print(f"Saved {self.db_id} to DB")
            else:
                with open(filename, 'wb' if PY2 else 'w') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.filename = filename

        except Exception as e:
            print(e)
            set_trace()
            raise LabelFileError(e)

    @staticmethod
    def is_label_file(filename):
        return osp.splitext(filename)[1].lower() == LabelFile.suffix
