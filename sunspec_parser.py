import xml.etree.ElementTree as ET
import sys

def lookup_data_type(data_type):

 data_types = {
    "uint16": "uint32",
    "int16" : "int32"
    } 

 if data_type in data_types:
    return data_types[data_type]
 else:
    return data_type



def main():
  with open(sys.argv[1], 'rt') as f:
      tree = ET.parse(f)
      root = tree.getroot()

  for num, element in enumerate(root.findall('model/block/point')):
      #print("#units = {}".format(element.get("units")))
      item = element.get("id")
      item_type = lookup_data_type( element.get("type") )
      label = root.find(''.join(['strings/point[@id="',item,'"]/label']))
      description = root.find(''.join(['strings/point[@id="',item,'"]/description']))
      notes = root.find(''.join(['strings/point[@id="',item,'"]/notes']))

      comment = ["// "]

      if(label is not None):
        if(label.text is not None):
          comment.append(label.text)
      if(description is not None):
        if(description.text is not None):
          comment.append(" - ")
          comment.append(description.text)
      if(notes is not None):
        if(notes.text is not None):
          comment.append(" - ")
          comment.append(notes.text)

      print("".join(comment))
      print("optional {} {} = {};".format(item_type, item, num+1))

      for num, symbol in enumerate(element.findall('symbol')):
        print("{} = {};".format(symbol.get("id"), symbol.text))

if __name__ == "__main__":
  main()
    