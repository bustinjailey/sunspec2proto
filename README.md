## Description
An XSLT file that understands sunspec xml files and converts them to proto fields. It will also include descriptions and notes, and put those as comments above the field attributes.

## Limitations
1. It does not handle custom types defined in sunspec
2. Not all types map one to one. Bit field values need to be broken out into individual booleans (not yet implemented)


## Usage (Node)

Sunspec to Proto (type fields only )
`npx xslt3 -xsl:sunspec_to_proto.xsl -s:smdx/smdx_64213.xml -o:out/smdx_64213.proto -t`

## Example
### In (smdx_64213.xml)
```
<sunSpecModels v="1">
  <!-- 64213: Generac Legacy Status Update -->
  <model id="64213" len="28" name="legacy_status">
    <block len="28" >
      <point id="VT_sf" offset="0" type="sunssf" mandatory="true" />
      <point id="I_sf"  offset="1" type="sunssf" mandatory="true" />      
      <point id="St"    offset="2" type="enum16" mandatory="true" >
        ...
      </point>        
      <point id="P"     offset="3" type="int16" mandatory="true" units="W"/>
      <point id="E"     offset="4" type="uint32" mandatory="true" units="Wh"/>
      <point id="Rb"    offset="6" type="bitfield16" mandatory="true" >
        ...
      </point>
      <point id="V"     offset="7" sf="VT_sf" type="int16" mandatory="true" units="V"/>
      <point id="I"     offset="8" sf="I_sf" type="int16" mandatory="true" units="A"/>
      <point id="T"     offset="9" sf="VT_sf" type="int16" mandatory="true" units="C"/>
      <point id="O0"    offset="10" type="uint16" mandatory="true" />
      <point id="O1"    offset="11" type="uint16" mandatory="true" />
      <point id="O2"    offset="12" type="uint16" mandatory="true" />
      ...
```

### Out (smdx_64213.proto)
```
// Model 64213: RCP Legacy Status Update
// Description: Status update data
// Notes:  (TODO: Hide if no notes)
message LegacyStatus {
            
    // Scale factor for V and T
    optional int32 VT_sf = 0;
            
    // Scale factor for I
    optional int32 I_sf = 1;
            
    // RCP state code
    optional enum16 St = 2;
            
    // REbus power (positive means the device is sourcing power onto REbus, negative means the device is sinking power from REbus) 
    optional int16 P = 3;
            
    // Total accumulated energy (exact definition differs by device)
    optional uint32 E = 4;
            
    // Status flags
    optional map<string, bool> Rb = 6;
            
    // REbus voltage
    optional int16 V = 7;
            
    // REbus current
    optional int16 I = 8;
            
    // Device temperature
    optional int16 T = 9;
            
    // Otherdata 0
    optional uint16 O0 = 10;
            
    // Otherdata 1
    optional uint16 O1 = 11;
            
    // Otherdata 2
    optional uint16 O2 = 12;
    
    ...
```
