import sys, json
from base64 import b64decode
from zlib import decompress
from lib.deserializer import payload_parser


def parse_p_strings(p_strings):
  for p_string in p_strings:
    suns_dict = payload_parser.payload_to_json(p_string)
    print("P-String Payloads \r\n {} \r\n".format(json.dumps(suns_dict, indent=1)))


def extract_payload(payload):
    zipped = b64decode(payload['z'])
    payload_bytes = decompress(zipped)
    payload = json.loads(payload_bytes)

    beacon_rcpn = payload['b']
    hosts = payload['h']
    # this is an inverter if len(hosts) > 0
    host_rcpn = hosts[0] if len(hosts) > 0 else None
    devices = payload['u']
    return beacon_rcpn, host_rcpn, devices

if __name__ == "__main__":
    with open(sys.argv[1], 'rt') as json_file:
        payload = json.load(json_file)
        output = extract_payload(payload)
        print("Sunspec Payload \r\n\r\n {} \r\n".format(json.dumps(output, indent=1)))
        
        for p_string in output[2]:
          parse_p_strings(p_string['p'])

       