from email.parser import BytesParser
from email.policy import default


def parse_multipart_form_data(content_type, body):
    parser_input = (
        f"Content-Type: {content_type}\r\n"
        "MIME-Version: 1.0\r\n"
        "\r\n"
    ).encode("utf-8") + body
    message = BytesParser(policy=default).parsebytes(parser_input)

    fields = {}
    for part in message.iter_parts():
        if part.get_content_disposition() != "form-data":
            continue

        field_name = part.get_param("name", header="content-disposition")
        if not field_name:
            continue

        payload = part.get_payload(decode=True) or b""
        fields[field_name] = {
            "filename": part.get_filename(),
            "bytes": payload,
            "text": payload.decode("utf-8", errors="replace"),
        }

    return fields
