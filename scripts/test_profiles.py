#!/usr/bin/env python3
"""Portable-profile regression tests; no private footage or network required."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from style_profile import (MARKER, build, check_overrides, defaults, import_profile, markdown, normalize_answers,
                           normalize_language, read_profile, resolve, suggestions_from_probe, validate)
from video_tools import caption_events, plan_cuts, whisper_language

HERE = Path(__file__).parent
FIXTURES = HERE / 'fixtures'
ROOT = HERE.parent
TRANSCRIPT = {'audio_duration_secs': 8, 'words': [
    {'text': 'Hello', 'start': 1.5, 'end': 2},
    {'text': 'world.', 'start': 5, 'end': 5.5}]}


def profile(answers):
    return build(answers)


def resolved(answers, job=None):
    return import_profile(profile(answers), job)[0]


class ProfileTests(unittest.TestCase):
    def test_round_trip_each_format(self):
        for orientation in ['vertical', 'landscape', 'square']:
            with self.subTest(orientation=orientation):
                answers = {'orientation': orientation, 'language': 'en'}
                prefs, overrides, migrated = read_profile(profile(answers))
                self.assertEqual(prefs, normalize_answers(answers)[0])
                self.assertEqual((overrides, migrated), ({}, None))
                self.assertEqual(resolved(answers)['format']['orientation'], orientation)

    def test_profile_is_sparse(self):
        text = profile({'captions': 'single_word', 'advanced': {'captions': {'font_size_px': 80}}})
        self.assertIn(MARKER, text)
        prefs, overrides, _ = read_profile(text)
        self.assertEqual(prefs, {'captions': 'single_word'})
        self.assertEqual(overrides, {'captions': {'font_size_px': 80}})

    def test_neutral_defaults_change_little(self):
        s = resolve({})
        self.assertEqual(s['content_type'], 'other')
        self.assertFalse(s['branding']['enabled'])
        self.assertFalse(s['hook']['enabled'])
        self.assertEqual((s['transitions']['style'], s['color']['style'], s['audio']['mix'], s['graphics']['mode']),
                         ('none', 'neutral', 'original', 'minimal'))
        self.assertEqual((s['pace']['style'], s['pace']['rhythm'], s['text_overlays']['mode']), ('gentle', 'scene', 'none'))
        self.assertEqual(s['language'], {'primary': 'auto', 'secondary': [], 'mode': 'auto'})

    def test_new_user_has_no_code_gino_identity(self):
        text = profile({}) + json.dumps(defaults())
        for private in ['Code Gino', 'carlogino.com', '@codegino', '#102B2D']:
            self.assertNotIn(private, text)

    def test_content_type_presets_and_precedence(self):
        montage = resolve({'content_type': 'montage'})
        self.assertEqual((montage['captions']['mode'], montage['pace']['rhythm'], montage['audio']['mix'], montage['color']['style']),
                         ('off', 'beat_sync', 'music_first', 'warm'))
        self.assertFalse(montage['delivery']['subtitles_srt'])
        self.assertEqual(resolve({'content_type': 'tutorial'})['format']['orientation'], 'landscape')
        explicit = resolve({'content_type': 'montage', 'captions': 'phrase_chunks'})
        self.assertEqual(explicit['captions']['mode'], 'phrase_chunks')
        head = resolve({'content_type': 'talking-head'})
        self.assertEqual((head['pace']['silence_threshold_seconds'], head['audio']['mix']), (1.25, 'voice_first'))

    def test_job_changes_override_without_touching_profile(self):
        text = profile({'content_type': 'vlog', 'captions': 'phrase_chunks'})
        job, _ = import_profile(text, {'captions': 'single_word', 'advanced': {'captions': {'font_size_px': 90}}})
        self.assertEqual((job['captions']['mode'], job['captions']['font_size_px']), ('single_word', 90))
        self.assertEqual(read_profile(text)[0]['captions'], 'phrase_chunks')
        self.assertEqual(import_profile(text, {'content_type': 'montage'})[0]['audio']['mix'], 'music_first')

    def test_language_forms(self):
        self.assertEqual(normalize_language('taglish'), {'primary': 'tl', 'secondary': ['en'], 'mode': 'fixed'})
        self.assertEqual(normalize_language('es'), {'primary': 'es', 'secondary': [], 'mode': 'fixed'})
        self.assertEqual(normalize_language('ask')['mode'], 'ask')
        self.assertEqual(normalize_language({'primary': 'es', 'secondary': ['en']})['mode'], 'fixed')
        for bad in ['Spanish!', {'primary': 'auto', 'mode': 'fixed'}, {'primary': 'en', 'secondary': ['en']},
                    {'primary': 'en', 'mode': 'sometimes'}, {'primary': 'en', 'extra': 1}, 7]:
            with self.subTest(bad=bad), self.assertRaises(ValueError): normalize_language(bad)

    def test_transcription_language(self):
        self.assertEqual(whisper_language('es'), 'es')
        self.assertIsNone(whisper_language('tl', ['en']))
        self.assertIsNone(whisper_language('auto'))
        self.assertIsNone(whisper_language('taglish'))
        self.assertEqual(whisper_language('english'), 'en')

    def test_v1_answer_aliases(self):
        prefs, _ = normalize_answers({'graphics': 'demonstrate', 'color': 'orange_teal', 'music': True})
        self.assertEqual(prefs, {'graphics': 'brief_driven', 'color': 'warm', 'audio_mix': 'voice_first'})

    def test_rotation_and_hdr_suggestions(self):
        p = {'streams': [{'codec_type': 'video', 'width': 1920, 'height': 1080, 'avg_frame_rate': '30000/1001',
             'color_transfer': 'arib-std-b67', 'side_data_list': [{'rotation': -90}]}, {'codec_type': 'audio'}]}
        result = suggestions_from_probe(p)
        self.assertEqual(result['suggested_answers']['orientation'], 'vertical')
        self.assertTrue(result['observations']['hdr'])
        self.assertTrue(result['observations']['has_audio'])
        self.assertAlmostEqual(result['observations']['source_fps'], 29.97003, places=4)
        self.assertNotIn('language', result['suggested_answers'])

    def test_square_no_audio_unknown_fps(self):
        r = suggestions_from_probe({'streams': [{'codec_type': 'video', 'width': 800, 'height': 800, 'avg_frame_rate': '0/0'}]})
        self.assertEqual(r['suggested_answers']['orientation'], 'square')
        self.assertFalse(r['observations']['has_audio'])
        self.assertIsNone(r['observations']['source_fps'])

    def test_no_video_rejected(self):
        with self.assertRaises(ValueError): suggestions_from_probe({'streams': []})

    def test_keep_all_changes_real_planner(self):
        edl, retimed = plan_cuts(TRANSCRIPT, resolve({'pace': 'keep_all'}))
        self.assertEqual(edl['removed_seconds'], 0)
        self.assertEqual(edl['keep_ranges'], [{'start': 0.0, 'end': 8.0}])
        self.assertEqual(retimed['words'][0]['start'], 1.5)

    def test_no_captions_disables_srt_and_events(self):
        s = resolve({'captions': 'off', 'delivery': 'editable'})
        self.assertFalse(s['delivery']['subtitles_srt'])
        self.assertTrue(s['delivery']['editable_project_zip'])
        self.assertEqual(caption_events(TRANSCRIPT, s), [])
        self.assertEqual(resolve({'captions': 'off', 'delivery': 'mp4_srt'})['delivery']['mode'], 'mp4')

    def test_single_word_profile(self):
        self.assertEqual([e['text'] for e in caption_events(TRANSCRIPT, resolve({'captions': 'single_word'}))], ['Hello', 'world.'])

    def test_overrides_only_reach_tunables(self):
        self.assertEqual(resolve({}, {'captions': {'font_size_px': 80}})['captions']['font_size_px'], 80)
        for patch in [{'captions': {'mode': 'off'}}, {'delivery': {'subtitles_srt': True}}, {'language': {'primary': 'en'}},
                      {'branding': {'website': 'x'}}, {'wrong': 1}, {'audio': {'mix': 'original'}}, {'captions': 3}]:
            with self.subTest(patch=patch), self.assertRaises(ValueError): check_overrides(patch)

    def test_unknown_answers_and_bad_types(self):
        for answer in [{'orientation': 'circle'}, {'music': 'false'}, {'advanced': {'wrong': 1}}, {'secret': 'x'},
                       {'palette': {'accent': 'red'}}, {'content_type': 'cartoon'}, {'fps': 500}, {'audio_mix': 'loud'}]:
            with self.subTest(answer=answer), self.assertRaises(ValueError): normalize_answers(answer)

    def test_bad_settings_are_rejected(self):
        patches = [{'format': {'width': 1921}}, {'format': {'width': 1920}}, {'captions': {'center_y_fraction': 2}},
                   {'captions': {'max_words': 0}}, {'captions': {'font_size_px': float('nan')}},
                   {'verification': {'beat_tolerance_frames': -1}}]
        for patch in patches:
            with self.subTest(patch=patch), self.assertRaises(ValueError): resolve({}, patch)

    def test_missing_nested_setting_fails_validation(self):
        s = resolve({}); del s['captions']['mode']
        with self.assertRaises(ValueError): validate(s)

    def test_prose_only_requires_assisted_import(self):
        with self.assertRaisesRegex(ValueError, 'assisted import'): read_profile('# My style\nUse short captions.')

    def test_bad_envelopes_rejected(self):
        text = profile({'captions': 'off'})
        for bad in [text+text, text.replace('"profile_version": 2', '"profile_version": 7'),
                    text.replace('"captions": "off"', '"captions": "loud"'),
                    text.replace('"overrides": {}', '"overrides": {"delivery": {"mode": "mp4"}}')]:
            with self.subTest(bad=bad[-120:]), self.assertRaises(ValueError): read_profile(bad)

    def test_update_keeps_existing_choices(self):
        text = build({'color': 'neutral'}, profile({'content_type': 'vlog', 'captions': 'single_word'}))
        self.assertEqual(read_profile(text)[0], {'content_type': 'vlog', 'captions': 'single_word', 'color': 'neutral'})


class V1MigrationTests(unittest.TestCase):
    EXPECTED = json.loads((FIXTURES / 'v1-expected.json').read_text())
    TRANSCRIPTS = json.loads((FIXTURES / 'transcripts.json').read_text())

    def load(self, name):
        return import_profile((FIXTURES / f'{name}.md').read_text())

    def test_v1_profiles_keep_their_editing_behaviour(self):
        for name, expected in self.EXPECTED.items():
            style, migrated = self.load(name)
            self.assertEqual((migrated, style['content_type']), ('v1', 'talking-head'))
            for transcript, want in zip(self.TRANSCRIPTS, expected):
                with self.subTest(name=name, words=len(transcript['words'])):
                    edl, retimed = plan_cuts(transcript, style)
                    self.assertEqual({k: edl[k] for k in want['edl']}, want['edl'])
                    got = [{k: e[k] for k in ['text', 'start', 'end', 'mode', 'center_y_fraction']} for e in caption_events(retimed, style)]
                    self.assertEqual(got, want['captions'])

    def test_v1_preferences_map_to_v2(self):
        custom, _ = self.load('v1-custom')
        self.assertEqual(custom['language'], {'primary': 'tl', 'secondary': ['en'], 'mode': 'fixed'})
        self.assertEqual((custom['graphics']['mode'], custom['color']['style'], custom['audio']['mix'], custom['transitions']['style']),
                         ('brief_driven', 'neutral', 'voice_first', 'none'))
        self.assertEqual((custom['captions']['font_size_px'], custom['branding']['palette']['accent']), (60, '#123456'))
        self.assertTrue(custom['delivery']['editable_project_zip'])
        self.assertFalse(custom['audio']['sound_effects'])
        neutral, _ = self.load('v1-neutral')
        self.assertEqual((neutral['transitions']['style'], neutral['color']['style'], neutral['graphics']['mode']), ('swipe', 'warm', 'balanced'))
        self.assertEqual(neutral['language']['mode'], 'ask')
        keep, _ = self.load('v1-keepall-square')
        self.assertEqual((keep['format']['orientation'], keep['delivery']['subtitles_srt'], keep['hook']['enabled']), ('square', False, False))

    def test_legacy_marker_imports(self):
        self.assertEqual(self.load('v1-legacy-marker')[0], self.load('v1-neutral')[0])

    def test_migrated_markdown_resolves_identically(self):
        for name in self.EXPECTED:
            with self.subTest(name=name):
                prefs, overrides, _ = read_profile((FIXTURES / f'{name}.md').read_text())
                v2 = markdown(prefs, overrides)
                self.assertIn(MARKER, v2)
                self.assertEqual(import_profile(v2), (self.load(name)[0], None))

    def test_code_gino_example_keeps_identity(self):
        style, migrated = import_profile((ROOT / 'examples' / 'code-gino.md').read_text())
        self.assertIsNone(migrated)
        self.assertEqual((style['branding']['website'], style['branding']['handle']), ('carlogino.com', '@codegino'))
        self.assertTrue(style['branding']['intro']['enabled'])
        self.assertEqual(style, self.load('v1-code-gino')[0])


class CliTests(unittest.TestCase):
    def run_cli(self, *args, cwd):
        return subprocess.run([sys.executable, *args], check=True, capture_output=True, text=True, cwd=cwd)

    def test_cross_session_cli_roundtrip_and_render_helpers(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            (p/'answers.json').write_text(json.dumps({'orientation': 'landscape', 'language': 'en', 'pace': 'keep_all'}))
            (p/'job.json').write_text(json.dumps({'captions': 'single_word'}))
            (p/'transcript.json').write_text(json.dumps(TRANSCRIPT))
            for cmd in [['style_profile.py', 'build', '--answers', str(p/'answers.json'), '--out', str(p/'style.md')],
                        ['style_profile.py', 'import', str(p/'style.md'), '--job', str(p/'job.json'), '--out', str(p/'job-style.json')],
                        ['video_tools.py', 'plan', str(p/'transcript.json'), '--style', str(p/'job-style.json'), '--out-dir', str(p/'plan')],
                        ['video_tools.py', 'captions', str(p/'plan/retimed.json'), '--style', str(p/'job-style.json'), '--out-dir', str(p/'captions')]]:
                self.run_cli(str(HERE/cmd[0]), *cmd[1:], cwd=tmp)
            job = json.loads((p/'job-style.json').read_text())
            self.assertEqual((job['format']['width'], job['language']['primary'], job['captions']['mode']), (1920, 'en', 'single_word'))
            self.assertEqual(json.loads((p/'plan/edl.json').read_text())['removed_seconds'], 0)
            self.assertIn('Hello', (p/'captions/captions.srt').read_text())

    def test_cli_migrate_and_upgrade_notice(self):
        with tempfile.TemporaryDirectory() as tmp:
            old = str(FIXTURES/'v1-custom.md')
            notice = self.run_cli(str(HERE/'style_profile.py'), 'import', old, '--out', 'a.json', cwd=tmp).stderr
            self.assertIn('upgraded from v1', notice)
            self.run_cli(str(HERE/'style_profile.py'), 'migrate', old, '--out', 'new.md', cwd=tmp)
            self.run_cli(str(HERE/'style_profile.py'), 'import', 'new.md', '--out', 'b.json', cwd=tmp)
            self.assertEqual((Path(tmp)/'a.json').read_text(), (Path(tmp)/'b.json').read_text())

    def test_cli_requires_selected_profile(self):
        result = subprocess.run([sys.executable, str(HERE/'video_tools.py'), 'plan', 'missing.json', '--out-dir', 'unused'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('--style', result.stderr)


if __name__ == '__main__': unittest.main()
