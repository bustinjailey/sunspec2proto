## Description
An XSLT file that understands sunspec xml files and converts them to proto fields. It will also include descriptions and notes, and put those as comments above the field attributes.

## Limitations
1. It does not handle custom types defined in sunspec
2. Not all types map one to one. Bit field values need to be broken out into individual booleans (not yet implemented)


## Usage (Node)

Sunspec to Proto (type fields only )
`npx xslt3 -xsl:sunspec_to_proto.xsl -s:smdx/smdx_64213.xml -o:out/smdx_64213.proto -t`
