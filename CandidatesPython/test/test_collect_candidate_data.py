import candidates.uniprot.collect_candidates as collector
import json
data_in = 'testdata/input/'

# # Mock ?
# test_list = ['Q4WF30', 'Q9BTE0', 'Q9HX72', 'Q9USR6', 'Q3UG98',
#              'Q9V9V9', 'P94482', 'O34569', 'O31995', 'A7SLC8',
#              'Q86II5', 'Q9BKR0', 'Q61FA3', 'P05332', 'P49855']

# Mock ?
# firmicutes_list = ['Q5HLX6', 'Q8CNE1', 'Q5HDT4', 'P99139', 'Q6G749', 'O31703', 'P65407', 'Q8NVA1', 'Q6GEG1']


def test_extract_annotations1():
    with open(data_in + 'P12345.json') as f:
        json_data = json.load(f)
    rec = collector.extract_annotations(json_data)
    assert rec['accession'] == 'P12345'
    assert 'Mammalia' in rec['SPOC']
    assert rec['DERF'] == 'Aspartate aminotransferase, mitochondrial'
    assert rec['DERS'][0] == 'mAspAT'
    assert '2.6.1.1' in rec['DEEC']
    assert 'Fatty acid-binding protein' in rec['DEAF']
    assert rec['GNNM'] == 'GOT2'
    assert 'Acetylation' in rec['SPKW']
    assert rec['CCCA'][0].split()[0] == 'RHEA:21824'
    assert 'Catalyzes the irreversible transamination of the ' + \
           'L-tryptophan metabolite L-kynurenine to form kynurenic acid (KA)' in rec['CCFU']
    assert 'Mitochondrion matrix' in rec['CCLO']


def test_extract_annotations2():
    with open(data_in + 'P36186.json') as f:
        json_data = json.load(f)
    record = collector.extract_annotations(json_data)
    assert 'Carbohydrate biosynthesis; gluconeogenesis' in record['CCPA']
    assert 'Belongs to the triosephosphate isomerase family' in record['CCSI']
    assert 'Homodimer' in record['CCSU']


def test_cofactor_json_format():
    with open(data_in + 'Q99V37.json') as f:
        json_data = json.load(f)
    record = collector.extract_annotations(json_data)
    assert len(record['CCCO']) == 4


def test_subcellular_location_json_format():
    with open(data_in + 'P61769.json') as f:
        json_data = json.load(f)
    record = collector.extract_annotations(json_data)
    assert len(record['CCLO']) == 4


def test_group_by_taxonomy():
    with open(data_in + 'IPR038987.json') as f:
        json_data = json.load(f)
    taxonomy_groups = collector.group_records_by_taxonomy_from_json(json_data)
    assert len(taxonomy_groups['Eukaryota Metazoa']) == 5


def test_cofactor_text_comment():
    with open(data_in + 'P0A431.json') as f:
        json_data = json.load(f)
    record = collector.extract_annotations(json_data)
    assert record['CCCO'][0] == 'PSII binds multiple chlorophylls, carotenoids and specific lipids'
