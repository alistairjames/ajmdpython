
from lxml import etree
import candidates.utils as utils
import logging
logger = logging.getLogger(__name__)


def create_interproid_to_memberid_map(xmlfilepath, outfilepath):
    """
    Extracts the InterPro ids and the signatures associated with these
    Generates a file mapping signature to InterPro id
    Created March 2018 and based on xml format for InterPro 72
    """
    outfile = open(outfilepath, 'w')
    record_count = 0
    context = etree.iterparse(xmlfilepath, events=('end',), tag='interpro')

    for event, interpro in context:
        id = interpro.attrib['id']
        record_count += 1
        for memberlist in interpro.getiterator('member_list'):
            for member in memberlist.getiterator('db_xref'):
                sig = member.attrib['dbkey']
                outfile.write('{0}\t{1}\n'.format(id, sig))

        # Tidy up after dealing with an entry tag
        interpro.clear()
        while interpro.getprevious() is not None:
            del interpro.getparent()[0]

    outfile.close()
    logger.info('Mapping for {0} InterProId to MemberId saved to {1}'.format(record_count, outfilepath))


def create_interproid_to_type_map(xmlfilepath, outfilepath):
    """
    Extracts InterPro identifiers and their type (Family, Domain, etc) from
    the interpro xml file previously downloaded from InterPro ftp site.
    """
    # filename = 'resources/interpro.xml'
    # outputfile = 'resources/interpro.xml.InterProId_Type.tsv'
    record_count = 0
    outfile = open(outfilepath, 'w')

    context = etree.iterparse(xmlfilepath, events=('end',), tag='interpro')

    for event, interpro in context:
        id = interpro.attrib['id']
        iptype = interpro.attrib['type']
        record_count += 1
        outfile.write('{0}\t{1}\n'.format(id, iptype))

        # Tidy up after dealing with an entry tag
        interpro.clear()
        while interpro.getprevious() is not None:
            del interpro.getparent()[0]

    outfile.close()
    logger.info('Mapping for {0} InterProId to Type saved to {1}'.format(record_count, outfilepath))


def get_family_nochild_interpro(xmlfilepath, outfilepath):
    """
    Extracts a list of all the InterPro Family identifiers that have no 'child_list'
    and have no HAMAP or PIRSF in the member db_xrefs from the xml file downloaded from InterPro ftp site.
    """
    outfile = open(outfilepath, 'w')
    record_count = 0
    context = etree.iterparse(xmlfilepath, events=('end',), tag='interpro')

    for event, interpro in context:
        id = interpro.attrib['id']
        iptype = interpro.attrib['type']
        childlist = interpro.find('child_list')
        if iptype == 'Family' and childlist is None:
            memberlist = interpro.find('member_list')
            if any(member.attrib['db'] in ('HAMAP', 'PIRSF') for member in memberlist.findall('db_xref')):
                continue
            else:
                record_count += 1
                outfile.write(id + '\n')

        # Tidy up after dealing with an entry tag
        interpro.clear()
        while interpro.getprevious() is not None:
            del interpro.getparent()[0]

    outfile.close()
    logger.info('Found {0} InterPro records with no children and no Hamap or PIR members'.format(record_count))

    """
    Combine three different files to create a list of InterPro Families that
    will be tested to see if they can be used for RuleBase rule creation.

    InterPro_MemberId.tsv which maps InterPro identifiers to the member database entries.
    InterPro_nochild_nohamap_nopir.list which lists all InterPro ids that meet the basic requirements for RuleBase rules
    Used_Signatures.list which lists the InterPro signatures and Member database signatures already used in UniRule
    """


def create_interpro_candidate_list(ipr_to_member_filepath, unirule_used_path,
                                   interpro_nochild_filepath, outfilepath):

    ip_members_map = get_member_map(ipr_to_member_filepath)
    used_sigs = utils.file_list_to_set(unirule_used_path)
    ip_candidate_list = []
    for ip_line in open(interpro_nochild_filepath):
        ip_candidate_list.append(ip_line.rstrip())

    filtered_candidates = __filter_candidates(ip_candidate_list, used_sigs, ip_members_map)
    outfile = open(outfilepath, 'w')
    outfile.write('\n'.join(filtered_candidates))
    outfile.close()

    logger.info('{0} candidates remaining after filtering {1} for used signatures'.format(
                                                                  len(filtered_candidates), len(ip_candidate_list)))


# Used only by create_interpro_candidate_list
# create two maps from the file, one from sig to ipr sig and another from ipr to a set of sigs
def get_member_map(filename):
    ipr_siglist_map = {}

    for line in open(filename):
        ipr, sig = line.rstrip().split('\t')
        if ipr not in ipr_siglist_map:
            ipr_siglist_map[ipr] = set()
        ipr_siglist_map[ipr].add(sig)

    return ipr_siglist_map


# Used only by create_interpro_candidate_list
def __filter_candidates(ip_candidates, used, ipsiglistmap):
    filtered = []
    for ip in ip_candidates:
        is_candidate = True
        if ip in used:
            is_candidate = False
        else:
            members = ipsiglistmap[ip]
            for member in members:
                if member in used:
                    is_candidate = False

        if is_candidate:
            filtered.append(ip)
    return filtered



