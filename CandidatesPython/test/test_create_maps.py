import candidates.interpro as interpro
import candidates.unirule as unirule
import os
data_in = os.sep.join(['data', 'test', 'input'])
data_out = os.sep.join(['data', 'test', 'output'])


def test_create_interproid_to_memberid_map():
    interpro_xmlpath = os.sep.join([data_in, 'short_interpro.xml'])
    test_outfilepath = os.sep.join([data_out, 'InterProId_MemberId_test_out.tsv'])
    interpro.create_interproid_to_memberid_map(interpro_xmlpath, test_outfilepath)
    test_lines = open(test_outfilepath).readlines()
    ipr, member = test_lines[5].rstrip().split('\t')
    assert len(test_lines) == 273
    assert ipr == 'IPR000006'
    assert member == 'PR00860'


def test_create_interproid_to_type_map():
    interpro_xmlpath = os.sep.join([data_in, 'short_interpro.xml'])
    test_outfilepath = os.sep.join([data_out, 'InterProId_Type_test_out.tsv'])
    interpro.create_interproid_to_type_map(interpro_xmlpath, test_outfilepath)
    test_lines = open(test_outfilepath).readlines()
    ipr, member = test_lines[5].rstrip().split('\t')
    assert len(test_lines) == 117
    assert ipr == 'IPR000009'
    assert member == 'family'


def test_get_family_nochild_interpro():
    interpro_xmlpath = os.sep.join([data_in, 'short_interpro.xml'])
    test_outfilepath = os.sep.join([data_out, 'InterPro_NoChild_test_out.list'])
    interpro.get_family_nochild_interpro(interpro_xmlpath, test_outfilepath)
    test_lines = open(test_outfilepath).readlines()
    ipr = test_lines[5].rstrip()
    assert len(test_lines) == 34
    assert ipr == 'IPR000044'


def test_get_used_unirule_signatures():
    unirule_urmlpath = os.sep.join([data_in, 'short_unirule-urml-latest.xml'])
    test_outfilepath = os.sep.join([data_out, 'used_signatures_from_urml_file.list'])
    unirule.collect_used_signatures(unirule_urmlpath, test_outfilepath)
    test_lines = open(test_outfilepath).readlines()
    assert len(test_lines) == 15
    assert test_lines[4].rstrip() == 'PF03211'

