import time
from unittest.mock import Mock

import candidates.uniprot.collect_candidates as collector


# Mock ?
def test_get_reviewed_jsonrecords_for_signature():
    json_records = collector.get_reviewed_uniprot_jsons_from_interpro_id('IPR038987')
    assert len(json_records) == 28


def test_get_uniprot_url_with_retry():
    requests = Mock()
    tries = 1
    url = 'url'
    headers = {}
    r = requests.get(url, headers=headers)
    if r.ok:
        return r
    else:
        while not r.ok and tries < 6:
            tries += 1
            time.sleep(3 ** tries)
            r = requests.get(url, headers=headers)
            if r.ok:
                if tries > 1:
                    print('Mock call_count: ' + requests.get.call_count)
                return r
        r.raise_for_status()
    print('Method calls: ' + requests.method_calls)


if __name__ == "__main__":
    test_get_uniprot_url_with_retry()




















# def test_get_from_jsonlist_and_group_by_taxonomy():
#     jsonrecords = lookup.get_reviewed_uniprot_json('IPR038987')
#     taxonomy_groups = collector.__group_records_by_taxonomy_from_json(jsonrecords)
#     assert len(taxonomy_groups['Eukaryota Metazoa']) == 5


# def test_cofactor_text_comment():
#     json_record = lookup.get_record_json('P0A431')
#     record = collector.__extract_annotations(json_record)
#     assert record['CCCO'][0] == 'PSII binds multiple chlorophylls, carotenoids and specific lipids'
