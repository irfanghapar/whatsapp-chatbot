from api.lead.listRecord import list_records

def check_record(phone):
    records = list_records()
    if records is not None:
        for record in records:
            fields = record.get('fields', {})
            if fields.get('Phone') == phone:
                print(f"Lead already exists for phone: {phone}")
                return record
    return None