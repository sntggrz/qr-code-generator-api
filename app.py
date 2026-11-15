import re
from io import BytesIO

import qrcode
from flask import Flask, request, send_file
from flasgger import Swagger
from flask_restful import Api, Resource
from qrcode.exceptions import DataOverflowError
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers.pil import CircleModuleDrawer, RoundedModuleDrawer

app = Flask(__name__)
api = Api(app)
Swagger(app)


class QrCode(Resource):
    def get(self):
        """
        This method responds to the GET request for generating a QR code for a given text.
        ---
        tags:
        - QR Code
        produces:
        - image/png
        parameters:
            - name: text
              in: query
              type: string
              required: true
              description: The text to be encoded in the QR code
            - name: fill_color
              in: query
              type: string
              required: false
              default: '000000'
              description: QR color as six hexadecimal digits, with or without #
            - name: back_color
              in: query
              type: string
              required: false
              default: 'FFFFFF'
              description: Background color as six hexadecimal digits, with or without #
            - name: box_size
              in: query
              type: integer
              required: false
              default: 10
              description: Pixels per QR square (1 to 20)
            - name: border
              in: query
              type: integer
              required: false
              default: 4
              description: Border width in QR squares (4 to 20)
            - name: error_correction
              in: query
              type: string
              required: false
              default: M
              enum: [L, M, Q, H]
              description: Error correction level
            - name: style
              in: query
              type: string
              required: false
              default: square
              enum: [square, rounded, circle]
              description: Shape of the QR squares
        responses:
            200:
                description: A successful GET request
                schema:
                    type: file
            400:
                description: Missing or invalid query parameter
        """
        text = request.args.get('text')
        if not text:
            return {"message": "Missing text query parameter"}, 400

        def integer_option(name, default, minimum, maximum):
            raw = request.args.get(name)
            if raw is None:
                return default
            try:
                value = int(raw)
            except ValueError:
                raise ValueError(f"{name} must be an integer from {minimum} to {maximum}")
            if not minimum <= value <= maximum:
                raise ValueError(f"{name} must be an integer from {minimum} to {maximum}")
            return value

        def color_option(name, default):
            raw = request.args.get(name, default).removeprefix('#')
            if not re.fullmatch(r'[0-9a-fA-F]{6}', raw):
                raise ValueError(f"{name} must be a six-digit hex color")
            return tuple(int(raw[index:index + 2], 16) for index in (0, 2, 4))

        try:
            box_size = integer_option('box_size', 10, 1, 20)
            border = integer_option('border', 4, 4, 20)
            fill_color = color_option('fill_color', '000000')
            back_color = color_option('back_color', 'FFFFFF')
        except ValueError as error:
            return {"message": str(error)}, 400

        correction = request.args.get('error_correction', 'M').upper()
        correction_levels = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H,
        }
        if correction not in correction_levels:
            return {"message": "error_correction must be L, M, Q, or H"}, 400

        style = request.args.get('style', 'square').lower()
        if style not in ('square', 'rounded', 'circle'):
            return {"message": "style must be square, rounded, or circle"}, 400

        qr = qrcode.QRCode(
            box_size=box_size,
            border=border,
            error_correction=correction_levels[correction],
        )
        try:
            qr.add_data(text)
            qr.make(fit=True)
        except DataOverflowError:
            return {"message": "text is too long for a QR code"}, 400

        if style == 'square':
            image = qr.make_image(fill_color=fill_color, back_color=back_color)
        else:
            drawers = {
                'rounded': RoundedModuleDrawer,
                'circle': CircleModuleDrawer,
            }
            image = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=drawers[style](),
                color_mask=SolidFillColorMask(
                    back_color=back_color,
                    front_color=fill_color,
                ),
            )

        image_file = BytesIO()
        image.save(image_file, format="PNG")
        image_file.seek(0)

        return send_file(image_file, mimetype="image/png")


api.add_resource(QrCode, "/qrcode")

if __name__ == "__main__":
    app.run(debug=True)
