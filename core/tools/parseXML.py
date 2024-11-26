import xml.etree.ElementTree as ET

def parseXML(filename):
    """
    Convert XML file to a Python dictionary structure.
    
    Parameters:
    filename (str): Path to the XML file.
    
    Returns:
    dict: A dictionary representation of the XML structure.
    """
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except ET.ParseError as e:
        raise ValueError(f"Failed to read XML file {filename}: {e}")
    
    # Recurse over child nodes
    theStruct = parseChildNodes(root)
    return theStruct

def parseChildNodes(theNode):
    """
    Recurse over node children and create a list of dictionaries.
    
    Parameters:
    theNode (xml.etree.ElementTree.Element): Current XML node.
    
    Returns:
    list: A list of dictionaries representing child nodes.
    """
    children = []
    for theChild in theNode:
        children.append(makeStructFromNode(theChild))
    return children

def makeStructFromNode(theNode):
    """
    Create a dictionary of node information.
    
    Parameters:
    theNode (xml.etree.ElementTree.Element): Current XML node.
    
    Returns:
    dict: A dictionary representing the node's data.
    """
    nodeStruct = {
        'Name': theNode.tag,
        'Attributes': parseAttributes(theNode),
        'Data': (theNode.text or '').strip(),
        'Children': parseChildNodes(theNode)
    }
    return nodeStruct

def parseAttributes(theNode):
    """
    Create a dictionary of attributes for an XML node.
    
    Parameters:
    theNode (xml.etree.ElementTree.Element): Current XML node.
    
    Returns:
    list: A list of dictionaries representing the attributes.
    """
    attributes = []
    for name, value in theNode.attrib.items():
        attributes.append({'Name': name, 'Value': value})
    return attributes
