import candidates.interpro as interpro
import candidates.uniprot.counter as uniprotcounter
data_in = 'data/test/input/'
data_out = 'data/test/output/'


def test_create_interpro_candidate_list():
    ipr_member_map_path = f'{data_in}stable_InterProId_MemberId.tsv'
    ipr_nochild_list_path = f'{data_in}stable_InterPro_NoChild.list'
    used_signatures_path = f'{data_in}short_usedSignatures.dat'
    test_outfilepath = f'{data_out}candidates_list_test.list'
    interpro.create_interpro_candidate_list(ipr_member_map_path, used_signatures_path,
                                            ipr_nochild_list_path, test_outfilepath)
    test_lines = open(test_outfilepath).readlines()
    assert len(test_lines) == 84
    assert test_lines[4].rstrip() == 'IPR000057'


def test_filter_candidates_by_hit_count():
    input_filepath = f'{data_in}stable_candidates_list.list'
    min_reviewed = 10
    min_unreviewed = 100
    test_outfilepath = f'{data_out}CandidateHitCounts_test.tsv'
    uniprotcounter.collect_counts(input_filepath, min_reviewed,
                                  min_unreviewed, test_outfilepath)
    test_lines = open(test_outfilepath).readlines()
    candidate, rev, unrev = test_lines[2].rstrip().split('\t')
    assert len(test_lines) == 4
    assert (candidate, rev, unrev) == ('IPR000247', '29', '1126')
