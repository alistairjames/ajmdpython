import os
import candidates.interpro as interpro
import candidates.uniprot.count_candidate_hits as uniprotcounter
import candidates.unirule as unirule
data_in = os.sep.join(['data', 'test', 'input'])
data_out = os.sep.join(['data', 'test', 'output'])


def test_create_interpro_candidate_list():
    ipr_member_map_path = os.sep.join([data_in, 'stable_InterProId_MemberId.tsv'])
    ipr_nochild_list_path = os.sep.join([data_in, 'stable_InterPro_NoChild.list'])
    unirule_rules_path = os.sep.join([data_in, 'short_unirule-urml-latest.xml'])
    unirule_used_path = os.sep.join([data_out, 'unirule_used.list'])
    test_outfilepath = os.sep.join([data_out, 'candidates_list_test.list'])
    unirule.collect_used_signatures(unirule_rules_path, unirule_used_path)
    interpro.create_interpro_candidate_list(ipr_member_map_path, unirule_used_path,
                                            ipr_nochild_list_path, test_outfilepath)
    test_lines = open(test_outfilepath).readlines()
    assert len(test_lines) == 82
    assert test_lines[4].rstrip() == 'IPR000057'


def test_filter_candidates_by_hit_count():
    input_filepath = os.sep.join([data_in, 'stable_candidates_list.list'])
    min_reviewed = 10
    min_unreviewed = 100
    test_outfilepath = os.sep.join([data_out, 'CandidateHitCounts_test.tsv'])
    uniprotcounter.collect_counts(input_filepath, min_reviewed,
                                  min_unreviewed, test_outfilepath)
    test_lines = open(test_outfilepath).readlines()
    candidate, rev, unrev = test_lines[2].rstrip().split('\t')
    assert len(test_lines) == 4
    assert (candidate, rev, unrev) == ('IPR000247', '29', '1126')
