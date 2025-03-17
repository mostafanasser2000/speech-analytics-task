import base64
from io import BytesIO
from typing import Dict

import constants
import magic
from flasgger import Swagger
from flask import Flask, jsonify, request
from mutagen.mp3 import MP3
from mutagen.ogg import OggFileType
from mutagen.wave import WAVE

app = Flask(__name__)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
    "title": "Audio Analysis API",
    "description": "API for analyzing audio files and extracting metadata",
    "version": "1.0.0",
}
swagger = Swagger(app, config=swagger_config)


def get_audio_info(file_content: str, file_type: str) -> Dict:
    FILE_FORMATS = {
        "audio/mpeg": MP3,
        "audio/wave": WAVE,
        "audio/x-wav": WAVE,
        "audio/wav": WAVE,
        "audio/ogg": OggFileType,
    }
    if file_type not in FILE_FORMATS:
        raise ValueError(f"Unsupported file type: {file_type}")

    audio_buffer = BytesIO(file_content)
    audio_class = FILE_FORMATS[file_type]
    audio = audio_class(audio_buffer)

    bit_depth = None
    if hasattr(audio.info, "bits_per_sample"):
        bit_depth = audio.info.bits_per_sample

    return {
        "duration": audio.info.length,
        "sample_rate": audio.info.sample_rate,
        "channels_count": audio.info.channels,
        "format": constants.SUPPORTED_FILE_TYPES[file_type],
        "bit_depth": bit_depth,
    }


def validate_file(data, binary=False):
    """
    Validates the provided file data.

    Args:
        data (dict): A dictionary containing the file data. Must include the key "audio".
        binary (bool, optional): A flag indicating whether the file is in binary format. Defaults to False.

    Returns:
        tuple: A tuple containing a boolean indicating success or failure, and a dictionary with error details or a tuple with file type and decoded file content.

    Raises:
        Exception: If there is an error processing the file.

    Errors:
        - {"error": "audio field is required"}: If the "audio" key is not present in the data.
        - {"error": "Invalid json data"}: If the data contains keys other than "audio".
        - {"error": "File size exceeds max limit (XMB)"}: If the file size exceeds the maximum allowed size.
        - {"error": "Invalid base64 value"}: If the base64 decoding fails.
        - {"error": "Not supported file format"}: If the file format is not supported.
        - {"error": "Error processing file"}: If there is an unspecified error during file processing.
    """
    try:
        if "audio" not in data:
            return False, {"error": "audio field is required"}

        keys = [key for key in data.keys()]
        if keys != ["audio"]:
            return False, {"error": "Invalid json data"}
        if binary:
            file = data["audio"]
            if file.content_length and file.content_length > constants.MAX_FILE_SIZE:
                return False, {
                    "error": f"File size exceeds max limit ({constants.MAX_FILE_SIZE // 1024 // 2024}MB)"
                }

            file_content = file.read()
            decoded_file = file_content
        else:
            file_content = data["audio"]
            try:
                decoded_file = base64.b64decode(file_content)
            except base64.binascii.Error:
                return False, {"error": "Invalid base64 value"}
            if len(decoded_file) > constants.MAX_FILE_SIZE:
                return False, {
                    "error": f"File size exceeds max limit ({constants.MAX_FILE_SIZE // 1024 // 2024}MB)"
                }
        file_type = magic.from_buffer(decoded_file, mime=True)
        if file_type not in constants.SUPPORTED_FILE_TYPES:
            return False, {"error": "Not supported file format"}

        return True, (file_type, decoded_file)

    except Exception:
        return False, {"error": "Error processing file"}


@app.route("/alive/")
def alive():
    """
    Check if the server is up.
    ---
    responses:
     200:
      description: Server is up
      schema:
        type: object
        properties:
         message:
          type: string
          example: alive
    """
    return jsonify({"message": "alive"}), 200


@app.route("/analyze-audio/", methods=["POST"])
def analyze_audio():
    """
    Take an audio file in base64 format and return its information.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            audio:
              type: string
              description: Base64 encoded audio file
    responses:
      200:
        description: Audio file analyzed successfully
        schema:
          type: object
          properties:
            duration:
              type: number
              description: Duration in seconds
              example: 12.3
            sample_rate:
              type: number
              example: 14400
            channels_count:
              type: number
              example: 1
            format:
              type: string
              example: "audio/wave"
            bit_depth:
              type: number
              example: 16
      400:
        description: Invalid input, Audio field is required, Invalid base64 value, Not supported audio format
      500:
        description: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data"}), 400

        is_valid, result = validate_file(data)

        if is_valid:
            file_type, decoded_file = result
            audio_info = get_audio_info(decoded_file, file_type=file_type)
            return jsonify(audio_info), 200
        else:
            return jsonify(result), 400
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@app.route("/analyze-binary-audio/", methods=["POST"])
def analyze_binary_audio():
    """
    Take an audio file  in binary format and return its information.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: audio
        in: formData
        type: file
        required: true
        description: Binary audio file
    responses:
      200:
        description: Audio file analyzed successfully
        schema:
          type: object
          properties:
            duration:
              type: number
              description: Duration in seconds
              example: 12.3
            sample_rate:
              type: number
              example: 14400
            channels_count:
              type: number
              example: 1
            format:
              type: string
              example: "audio/wave"
            bit_depth:
              type: number
              example: 16
      400:
        description: Invalid input, Audio field is required, Invalid base64 value, Not supported audio format
      500:
        description: Internal server error
    """
    try:
        if not request.files:
            return jsonify({"error": "No file uploaded"}), 400
        is_valid, result = validate_file(request.files, binary=True)
        if is_valid:
            file_type, decoded_file = result
            audio_info = get_audio_info(decoded_file, file_type=file_type)
            return jsonify(audio_info), 200

        return jsonify(result), 400

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@app.route("/")
def docs():
    from flask import redirect

    redirect("/docs/")


if __name__ == "__main__":
    app.run(debug=True)
