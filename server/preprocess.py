import pandas as pd
import re
from xml.etree.ElementTree import fromstring

def parse_log(log_xml):
    """Parse an XML log into a dictionary."""
    root = fromstring(log_xml)
    event_data = {}

    # Parse System data
    system = root.find("{http://schemas.microsoft.com/win/2004/08/events/event}System")
    if system is not None:
        for child in system:
            event_data[child.tag.split('}')[-1]] = child.text

    # Parse EventData
    eventdata = root.find("{http://schemas.microsoft.com/win/2004/08/events/event}EventData")
    if eventdata is not None:
        for data in eventdata:
            name = data.attrib.get("Name")
            event_data[name] = data.text

    return event_data

def preprocess_logs(log_xml):
    """Preprocess log XML into a structured DataFrame-ready dictionary."""
    parsed_data = parse_log(log_xml)

    # Ensure specific fields exist
    fields = ['EventRecordID', 'ProcessId', 'EventID', 'User', 'Image', 'CommandLine', 'Protocol']
    for field in fields:
        if field not in parsed_data:
            parsed_data[field] = None

    # Extract additional features
    parsed_data['binary'] = (
        parsed_data['Image'].split('\\')[-1].lower() if parsed_data['Image'] else "unknown"
    )
    parsed_data['path'] = (
        '\\'.join(parsed_data['Image'].split('\\')[:-1]).lower() if parsed_data['Image'] else "unknown"
    )
    parsed_data['arguments'] = (
        ' '.join(parsed_data['CommandLine'].split()[1:]) if parsed_data['CommandLine'] else "empty"
    )

    # Add regex-based features
    parsed_data['b64'] = int(bool(re.search(r"[a-zA-Z0-9+/]{64,}={0,2}", parsed_data['arguments'])))
    parsed_data['unc_url'] = int(bool(re.search(r"\\\\[a-zA-Z0-9]+\\[a-zA-Z0-9\\]+", parsed_data['arguments'])))
    parsed_data['url'] = int(bool(re.search(r"https?://", parsed_data['arguments'])))
    parsed_data['network'] = int(parsed_data['Protocol'] is not None)

    return parsed_data
