"""Validate an editorial timeline; content and performance still require review."""
import json
import sys
from fractions import Fraction
from pathlib import Path


def integer(value, label, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f'{label}: expected integer >= {minimum}')
    return value


def union_length(intervals):
    end = None
    total = 0
    for a, b in sorted(intervals):
        if end is None or a > end:
            total += b - a
            end = b
        elif b > end:
            total += b - end
            end = b
    return total


def validate(data, base_dir):
    if not isinstance(data, dict):
        raise ValueError('timeline must be an object')
    fps = data.get('fps', {})
    if not isinstance(fps, dict):
        raise ValueError('fps must be an object')
    rate = Fraction(integer(fps.get('num'), 'fps.num', 1), integer(fps.get('den'), 'fps.den', 1))
    duration = integer(data.get('duration_frames'), 'duration_frames', 1)
    stage = data.get('maturity')
    evidence = data.get('validated_through')
    if stage not in ('A0', 'A1', 'A2', 'A3') or evidence not in ('A0', 'A1', 'A2'):
        raise ValueError('invalid maturity / validated_through')
    if stage != 'A3' and stage != evidence:
        raise ValueError('maturity must match validated_through before delivery snapshot')
    base = Path(base_dir)

    def file_required(row, key):
        value = row.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{key}: file evidence missing')
        path = Path(value)
        if not path.is_absolute():
            path = base / path
        if not path.is_file():
            raise ValueError(f'{key}: file evidence unavailable')

    def rows(key, required=False):
        values = data.get(key, [])
        if not isinstance(values, list) or (required and not values):
            raise ValueError(f'{key}: expected nonempty list' if required else f'{key}: expected list')
        seen = set()
        for row in values:
            if not isinstance(row, dict):
                raise ValueError(f'{key}: row must be an object')
            rid = row.get('id')
            if not isinstance(rid, str) or not rid.strip() or rid in seen:
                raise ValueError(f'{key}: missing or duplicate id')
            seen.add(rid)
            a = integer(row.get('in'), f'{rid}.in')
            b = integer(row.get('out'), f'{rid}.out')
            if not a < b <= duration:
                raise ValueError(f'{rid}: interval outside scene or empty')
        return values

    cues = rows('cues')
    shots = rows('shots', required=True)
    events = rows('events')
    for cue in cues:
        for key in ('speaker', 'text', 'spoken_text'):
            if not isinstance(cue.get(key), str) or not cue[key].strip():
                raise ValueError(f'{cue["id"]}: {key} missing')
        if cue.get('timing_basis') not in ('estimate', 'measured'):
            raise ValueError(f'{cue["id"]}: invalid timing_basis')
        if evidence in ('A1', 'A2') and cue['timing_basis'] != 'measured':
            raise ValueError(f'{cue["id"]}: estimated cue cannot support {evidence}')
        if cue['timing_basis'] == 'measured':
            file_required(cue, 'audio_path')
            if not isinstance(cue.get('measurement_note'), str) or not cue['measurement_note'].strip():
                raise ValueError(f'{cue["id"]}: measurement_note missing')
    cursor = 0
    for shot in sorted(shots, key=lambda x: x['in']):
        if shot['in'] != cursor:
            raise ValueError('primary shot track must cover scene without gaps or overlaps')
        cursor = shot['out']
        refs = shot.get('cue_ids', [])
        if not isinstance(refs, list) or any(not isinstance(x, str) for x in refs) or len(refs) != len(set(refs)):
            raise ValueError(f'{shot["id"]}: invalid cue_ids')
        expected = {c['id'] for c in cues if max(c['in'], shot['in']) < min(c['out'], shot['out'])}
        if set(refs) != expected:
            raise ValueError(f'{shot["id"]}: cue_ids must match intersecting cues (including sound bridges)')
    if cursor != duration:
        raise ValueError('primary shot track does not reach scene end')
    if evidence == 'A2':
        file_required(data, 'animatic_path')
        if not isinstance(data.get('review_note'), str) or not data['review_note'].strip():
            raise ValueError('A2 review_note missing')
    handles = data.get('handles', {})
    if not isinstance(handles, dict):
        raise ValueError('handles must be an object')
    head = integer(handles.get('head_frames', 0), 'head_frames')
    tail = integer(handles.get('tail_frames', 0), 'tail_frames')
    occupied = union_length([(x['in'], x['out']) for x in cues + events])
    cue_union = union_length([(x['in'], x['out']) for x in cues])
    def seconds(frames):
        return float(Fraction(frames, 1) / rate)
    return {'duration_frames': duration, 'duration_seconds': seconds(duration),
            'cue_union_frames': cue_union, 'cue_union_seconds': seconds(cue_union),
            'cue_and_event_union_frames': occupied, 'unoccupied_frames': duration - occupied,
            'cue_and_event_union_seconds': seconds(occupied), 'unoccupied_seconds': seconds(duration - occupied),
            'generation_frames_with_package_handles': duration + head + tail,
            'generation_seconds_with_package_handles': seconds(duration + head + tail),
            'maturity': stage, 'validated_through': evidence,
            'limit': 'Structure and file presence only; no listening, visual or semantic verification.'}


def main():
    try:
        source = Path(sys.argv[1])
        result = validate(json.loads(source.read_text(encoding='utf-8-sig')), source.parent)
    except (ValueError, KeyError, TypeError, OSError, IndexError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps({'ok': True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
