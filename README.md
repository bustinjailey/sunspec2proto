## Description
A tool that takes in sunspec xml files and converts them to proto fields. It will also scan for description and notes, and put those as comments above the field attributes.



## Limitations
1. It does not create message types
2. It does not handle custom types defined in sunspec
3. Not all types map one to one, example. Bit fields need to be converted to uint32


## Usage ( Python 3.7 )

Sunspec to Proto ( type fields only )
`python sunspec_to_proto.py smdx_00804.xml`


Sunspec Payload Decoder
`python sunspec_parser.py payloads/common_model.json`
`python sunspec_parser.py payloads/site_energy.json`
