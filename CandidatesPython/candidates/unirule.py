'''
Collect all the signatures already used in positive conditions in UniRule rules.
The reference to the unirule xsd may need updating. This script was tested in March 2018 
The list includes InterPro signatures used as well as individual member database signatures
'''

from lxml import etree
import logging
logger = logging.getLogger(__name__)


# Convert bare tag to full name for use in the query
def full_tag(tag):
    t = str(etree.QName('http://uniprot.org/urml/rules', tag))
    return t


def collect_used_signatures(rules_xml_filepath, outfilepath):
    allsigset = set()
    outfile = open(outfilepath, 'w')

    context = etree.iterparse(rules_xml_filepath, events=('end',), tag=full_tag('rule'))
    for event, rule in context:
        conditions = rule.find(full_tag('conditions'))
        conditionset = conditions.findall('.//' + full_tag('condition'))
        for condition in conditionset:
            if condition.attrib.get('exists') == 'false':
                continue
            else:
                if condition.attrib.get('on') == 'fact:ProteinSignature':
                    fields = condition.findall('.//' + full_tag('field'))
                    for field in fields:
                        if field.attrib.get('attribute') == 'value':
                            sig = field.text
                            allsigset.add(sig)

        rule.clear()
        while rule.getprevious() is not None:
            del rule.getparent()[0]
    for s in sorted(allsigset):
        outfile.write(s + '\n')
    outfile.close()
    logger.info('{0} signatures already used in rules saved to {1}'.format(len(allsigset), outfilepath))



