from copy import deepcopy
from fractions import Fraction
from scripts.timing_check import validate


def sample():
    return {'fps': {'num': 24, 'den': 1}, 'duration_frames': 240,
            'maturity': 'A0', 'validated_through': 'A0',
            'cues': [{'id': 'D01', 'speaker': '妈妈', 'text': '把门留着，我一会儿回来。',
                      'spoken_text': '把门留着，我一会儿回来。', 'in': 24, 'out': 96, 'timing_basis': 'estimate'},
                     {'id': 'D02', 'speaker': '阿岚', 'text': '钥匙呢？', 'spoken_text': '钥匙呢？',
                      'in': 84, 'out': 120, 'timing_basis': 'estimate'}],
            'shots': [{'id': 'S01', 'in': 0, 'out': 48, 'cue_ids': ['D01']},
                      {'id': 'S02', 'in': 48, 'out': 240, 'cue_ids': ['D01', 'D02']}],
            'events': [{'id': 'E01', 'in': 144, 'out': 192, 'description': '门被风推开，钥匙落在地上。'}],
            'handles': {'head_frames': 12, 'tail_frames': 24}}


def rejected(data, base):
    try:
        validate(data, base)
    except ValueError:
        return
    raise AssertionError('invalid timeline accepted')


def test_overlap_silence_and_handles(tmp_path):
    r = validate(sample(), tmp_path)
    assert r['duration_seconds'] == 10
    assert r['cue_union_frames'] == 96
    assert r['cue_and_event_union_frames'] == 144
    assert r['unoccupied_frames'] == 96
    assert r['generation_frames_with_package_handles'] == 276
    assert r['cue_union_seconds'] == 4
    assert r['cue_and_event_union_seconds'] == 6
    assert r['unoccupied_seconds'] == 4
    assert r['generation_seconds_with_package_handles'] == 11.5


def test_cross_shot_cue_cannot_disappear(tmp_path):
    d = sample()
    d['shots'][1]['cue_ids'] = ['D02']
    rejected(d, tmp_path)


def test_estimate_cannot_be_promoted(tmp_path):
    d = sample()
    d['maturity'] = d['validated_through'] = 'A1'
    rejected(d, tmp_path)
    d['maturity'] = 'A3'
    rejected(d, tmp_path)
    d['validated_through'] = 'A0'
    assert validate(d, tmp_path)['validated_through'] == 'A0'


def test_measured_requires_accessible_file(tmp_path):
    d = sample()
    d['cues'][0].update(timing_basis='measured', audio_path='missing.wav', measurement_note='波形起止待核对')
    rejected(d, tmp_path)


def test_rational_fps(tmp_path):
    d = sample()
    d['fps'] = {'num': 24000, 'den': 1001}
    assert validate(d, tmp_path)['duration_seconds'] == float(Fraction(240 * 1001, 24000))


def test_bad_intervals_and_duplicate_ids(tmp_path):
    for change in ('negative', 'empty', 'bool', 'duplicate', 'gap', 'reference'):
        d = deepcopy(sample())
        if change == 'negative': d['handles']['head_frames'] = -1
        elif change == 'empty': d['cues'][0]['out'] = d['cues'][0]['in']
        elif change == 'bool': d['duration_frames'] = True
        elif change == 'duplicate': d['cues'][1]['id'] = 'D01'
        elif change == 'gap': d['shots'][1]['in'] = 49
        elif change == 'reference': d['shots'][0]['cue_ids'].append('不存在的台词')
        rejected(d, tmp_path)
