#!/usr/bin/env python3
"""Portable-profile regression tests; no private footage or network required."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from style_profile import apply_answers, base_style, import_markdown, markdown, suggestions_from_probe, validate
from video_tools import caption_events, plan_cuts

TRANSCRIPT = {'audio_duration_secs': 8, 'words': [
    {'text': 'Hello', 'start': 1.5, 'end': 2},
    {'text': 'world.', 'start': 5, 'end': 5.5}]}


class ProfileTests(unittest.TestCase):
    def test_round_trip_each_format(self):
        for orientation in ['vertical','landscape','square']:
            with self.subTest(orientation=orientation):
                s=apply_answers(base_style(),{'orientation':orientation,'language':'english'})
                self.assertEqual(import_markdown(markdown(s)),s)

    def test_new_user_has_no_code_gino_identity(self):
        text=markdown(base_style())
        for private in ['Code Gino','carlogino.com','@codegino']:
            self.assertNotIn(private,text)
        self.assertFalse(base_style()['branding']['enabled'])

    def test_explicit_preset_preserves_identity(self):
        s=base_style('code-gino')
        self.assertEqual(s['branding']['website'],'carlogino.com')
        self.assertTrue(s['branding']['intro']['enabled'])
        self.assertEqual(import_markdown(markdown(s)),s)

    def test_rotation_and_hdr_suggestions(self):
        p={'streams':[{'codec_type':'video','width':1920,'height':1080,'avg_frame_rate':'30000/1001',
            'color_transfer':'arib-std-b67','side_data_list':[{'rotation':-90}]},{'codec_type':'audio'}]}
        result=suggestions_from_probe(p)
        self.assertEqual(result['suggested_answers']['orientation'],'vertical')
        self.assertTrue(result['observations']['hdr'])
        self.assertTrue(result['observations']['has_audio'])
        self.assertAlmostEqual(result['observations']['source_fps'],29.97003,places=4)
        self.assertNotIn('language',result['suggested_answers'])

    def test_square_no_audio_unknown_fps(self):
        r=suggestions_from_probe({'streams':[{'codec_type':'video','width':800,'height':800,'avg_frame_rate':'0/0'}]})
        self.assertEqual(r['suggested_answers']['orientation'],'square')
        self.assertFalse(r['observations']['has_audio'])
        self.assertIsNone(r['observations']['source_fps'])

    def test_no_video_rejected(self):
        with self.assertRaises(ValueError): suggestions_from_probe({'streams':[]})

    def test_keep_all_changes_real_planner(self):
        s=apply_answers(base_style(),{'pace':'keep_all'})
        edl,retimed=plan_cuts(TRANSCRIPT,s)
        self.assertEqual(edl['removed_seconds'],0)
        self.assertEqual(edl['keep_ranges'],[{'start':0.0,'end':8.0}])
        self.assertEqual(retimed['words'][0]['start'],1.5)

    def test_no_captions_disables_srt_and_events(self):
        s=apply_answers(base_style(),{'captions':'off','delivery':'editable'})
        self.assertFalse(s['delivery']['subtitles_srt'])
        self.assertTrue(s['delivery']['editable_project_zip'])
        self.assertEqual(caption_events(TRANSCRIPT,s),[])

    def test_single_word_profile(self):
        s=apply_answers(base_style(),{'captions':'single_word'})
        self.assertEqual([e['text'] for e in caption_events(TRANSCRIPT,s)],['Hello','world.'])

    def test_sound_and_color_switches(self):
        s=apply_answers(base_style(),{'music':False,'sound_effects':False,'color':'neutral','transitions':'none'})
        self.assertEqual(s['sound']['effects'],[])
        self.assertFalse(s['transitions']['whoosh'])
        self.assertFalse(s['transitions']['enabled'])
        self.assertFalse(s['color']['warm_skin'])

    def test_advanced_changes_and_input_immutable(self):
        s=base_style(); original=copy.deepcopy(s)
        result=apply_answers(s,{'advanced':{'captions':{'font_size_px':80}}})
        self.assertEqual(result['captions']['font_size_px'],80)
        self.assertEqual(s,original)

    def test_unknown_answers_and_bad_types(self):
        for answer in [{'orientation':'circle'},{'music':'false'},{'advanced':{'wrong':1}}, {'secret':'x'}, {'palette':{'accent':'red'}}]:
            with self.subTest(answer=answer), self.assertRaises(ValueError): apply_answers(base_style(),answer)

    def test_bad_settings_are_rejected(self):
        patches=[{'format':{'width':1921}}, {'format':{'width':1920}}, {'captions':{'center_y_fraction':2}},
                 {'captions':{'max_words':0}}, {'captions':{'font_size_px':float('nan')}},
                 {'delivery':{'publish_automatically':True}}, {'sound':{'replacement_narration':True}}]
        for patch in patches:
            with self.subTest(patch=patch), self.assertRaises(ValueError): apply_answers(base_style(),{'advanced':patch})

    def test_missing_nested_setting_fails_import(self):
        s=base_style(); del s['captions']['mode']
        with self.assertRaises(ValueError):validate(s)

    def test_prose_only_requires_assisted_import(self):
        with self.assertRaisesRegex(ValueError,'assisted import'):import_markdown('# My style\nUse short captions.')

    def test_duplicate_and_unsupported_version_rejected(self):
        text=markdown(base_style())
        for bad in [text+text,text.replace('"profile_version": 1','"profile_version": 7')]:
            with self.assertRaises(ValueError):import_markdown(bad)

    def test_cross_session_cli_roundtrip_and_render_helpers(self):
        scripts=Path(__file__).parent
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            (p/'answers.json').write_text(json.dumps({'orientation':'landscape','language':'english','pace':'keep_all'}))
            (p/'transcript.json').write_text(json.dumps(TRANSCRIPT))
            cmds=[['style_profile.py','build','--answers',str(p/'answers.json'),'--out',str(p/'style.md')],
                  ['style_profile.py','import',str(p/'style.md'),'--out',str(p/'resolved.json')],
                  ['video_tools.py','plan',str(p/'transcript.json'),'--style',str(p/'resolved.json'),'--out-dir',str(p/'plan')],
                  ['video_tools.py','captions',str(p/'plan/retimed.json'),'--style',str(p/'resolved.json'),'--out-dir',str(p/'captions')]]
            for cmd in cmds:
                subprocess.run([sys.executable,str(scripts/cmd[0]),*cmd[1:]],check=True,capture_output=True,text=True,cwd=tmp)
            resolved=json.loads((p/'resolved.json').read_text())
            self.assertEqual(resolved['format']['width'],1920)
            self.assertEqual(resolved['language']['default'],'english')
            self.assertEqual(json.loads((p/'plan/edl.json').read_text())['removed_seconds'],0)
            self.assertIn('Hello',(p/'captions/captions.srt').read_text())

    def test_cli_requires_selected_profile(self):
        command=[sys.executable,str(Path(__file__).with_name('video_tools.py')),'plan','missing.json','--out-dir','unused']
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('--style',result.stderr)


if __name__=='__main__':unittest.main()
