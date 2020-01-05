import datetime


def parse_date_input(date_object: object) -> str:
    """
    accepts datetime, date objects or date formatted strings (eg 1/2/19);  should be able to handle most regional
    format variations.
    Returns an ISO 8601 formatted date string
     :type date_object: object
    """
    iso_formatted_string: str
    if isinstance(date_object, datetime.datetime):
        iso_formatted_string = datetime.datetime(date_object).isoformat(timespec='seconds')
    elif isinstance(date_object, datetime.date):
        iso_formatted_string = datetime.date(date_object).isoformat()
    else:
        input_datetime: datetime.datetime
        input_datetime = None
        sep_chars = {'-', '/'}
        date_formats_order = {'M|D|Y', 'D|M|Y', 'Y|M|D'}
        for ordr in date_formats_order:
            if input_datetime is not None:
                break
            else:
                for sep in sep_chars:
                    result: datetime.datetime

                    try:
                        form = ordr.replace('|', sep).replace('M', '%m').replace('Y', '%y').replace('D', '%d')
                        result = datetime.datetime.strptime(date_object, form)
                    except ValueError:
                        try:
                            form = ordr.replace('|', sep).replace('M', '%m').replace('Y', '%Y').replace('D', '%d')
                            result = datetime.datetime.strptime(date_object, form)
                        except ValueError:
                            result = None
                            pass
                    finally:
                        if result is not None:
                            input_datetime = result
                            break
        if input_datetime is not None:
            iso_formatted_string = input_datetime.isoformat()
        else:
            raise TypeError
    return iso_formatted_string


def dict_to_json(args: dict) -> str:
    """

    :rtype: object
    """
    if args is None or len(args) == 0:
        return None
    else:
        json_body = "{"
        for key, value in args.items():
            if isinstance(value, list):
                json_body += f'\"{key}\": ['
                for i in value:
                    if isinstance(i, int):
                        json_body += f'{i}, '
                    elif isinstance(i, bool):
                        if bool(i):
                            json_body += 'true, '
                        else:
                            json_body += 'false, '
                    else:
                        json_body += f'\"{i}\", '
                json_body = json_body.rstrip(', ')
                json_body += ']'
            else:
                json_body += f'\"{key}\":\"{value}\", '
        json_body = json_body.rstrip(', ')
        json_body += "}"
        return json_body


def parse_json_item(item: object) -> str:
    if isinstance(item, int):
        return str(item)
    elif isinstance(item, bool):
        if bool(item):
            return 'true'
        else:
            return 'false'
    elif isinstance(item, list):
        return parse_json_list(item)
    elif isinstance(item, dict):
        return dict_to_json(item)


def parse_json_list(litem: list) -> str:
    json_item = '['
    for li in litem:
        json_item += parse_json_item(li) + ', '
    json_item += ']'
    return json_item
