#!/usr/bin/env python3
"""Deterministic helper checks; not a substitute for reviewing a rendered edit."""
import copy
import json
import tempfile
import unittest
import wave
from pathlib import Path
from video_tools import DEFAULT_STYLE, plan_cuts, caption_events
from make_sfx import make

STYLE=json.loads(DEFAULT_STYLE.read_text())


def transcript(words,duration=10):
    return {'audio_duration_secs':duration,'words':[{'text':t,'start':s,'end':e} for t,s,e in words]}


class EditingChecks(unittest.TestCase):
    def test_short_pauses_and_edges_remain(self):
        raw=transcript([('Hello',.2,.8),('world.',1.1,1.7)],2.0)
        edl,out=plan_cuts(raw,STYLE)
        self.assertEqual(edl['delete_ranges'],[])
        self.assertEqual(out['words'][1]['start'],1.1)

    def test_long_pause_retains_natural_breath(self):
        raw=transcript([('Hello',.2,1.0),('world.',4.0,5.0)],5.4)
        edl,out=plan_cuts(raw,STYLE)
        self.assertAlmostEqual(out['words'][1]['start']-out['words'][0]['end'],.45)
        for word in raw['words']:
            self.assertTrue(any(k['start']<=word['start'] and k['end']>=word['end'] for k in edl['keep_ranges']))

    def test_word_guards_override_short_breath(self):
        style=copy.deepcopy(STYLE)
        style['pace']['word_guard_seconds']=.3
        style['pace']['retained_pause_seconds']=.1
        edl,out=plan_cuts(transcript([('A',.2,1),('B',4,5)],5.2),style)
        self.assertAlmostEqual(out['words'][1]['start']-out['words'][0]['end'],.6)

    def test_overlapping_asr_tokens_preserve_speech(self):
        raw=transcript([('A',.1,3),('B',.4,.7),('C',2.9,3.5)],4)
        edl,_=plan_cuts(raw,STYLE)
        self.assertEqual(edl['delete_ranges'],[])

    def test_no_speech_preserves_full_video(self):
        edl,out=plan_cuts(transcript([],8),STYLE)
        self.assertEqual(edl['keep_ranges'],[{'start':0.,'end':8.}])
        self.assertEqual(out['words'],[])

    def test_default_is_natural_phrase_chunk(self):
        raw=transcript([('Ngayon',.2,.5),('try',.52,.7),('natin.',.75,1.1)],1.5)
        events=caption_events(raw,STYLE)
        self.assertEqual([e['text'] for e in events],['Ngayon try natin.'])
        self.assertEqual(events[0]['start'],.2)
        self.assertEqual(len(events[0]['words']),3)
        self.assertNotIn('pop_seconds',events[0])
        self.assertTrue(all(e['color']=='#FFFFFF' for e in events))

    def test_explicit_single_word_override(self):
        style=copy.deepcopy(STYLE);style['captions']['mode']='single_word'
        events=caption_events(transcript([('Try',.2,.5),('natin.',.52,.8)],1),style)
        self.assertEqual([e['text'] for e in events],['Try','natin.'])
        self.assertTrue(all('pop_seconds' in e for e in events))
        self.assertLessEqual(events[0]['end'],events[1]['start'])

    def test_sentence_and_clause_boundaries(self):
        tokens=['Try','natin','ito,','tapos','next.','Okay?']
        events=caption_events(transcript([(t,i*.25,i*.25+.2) for i,t in enumerate(tokens)],2),STYLE)
        self.assertEqual([e['text'] for e in events],['Try natin ito,','tapos next.','Okay?'])

    def test_acronym_does_not_force_sentence_break(self):
        events=caption_events(transcript([('A.I.',0,.3),('video',.31,.6),('editing.',.61,.9)],1.2),STYLE)
        self.assertEqual(events[0]['text'],'A.I. video editing.')

    def test_max_words_and_source_word_coverage(self):
        raw=transcript([(f'w{i}',i*.2,i*.2+.15) for i in range(14)],4)
        events=caption_events(raw,STYLE)
        self.assertEqual([len(e['words']) for e in events],[6,6,2])
        self.assertEqual([w['text'] for e in events for w in e['words']], [w['text'] for w in raw['words']])
        self.assertTrue(all(a['end']<=b['start'] for a,b in zip(events,events[1:])))

    def test_pause_break_is_not_held_across_silence(self):
        events=caption_events(transcript([('Hello',0,.2),('there',.25,.5),('Next',1.3,1.6)],2),STYLE)
        self.assertEqual([e['text'] for e in events],['Hello there','Next'])
        self.assertAlmostEqual(events[0]['end'],.68)

    def test_duration_cap_splits_long_phrase(self):
        raw=transcript([(f'w{i}',i*.8,i*.8+.7) for i in range(6)],5)
        events=caption_events(raw,STYLE)
        self.assertTrue(all(e['words'][-1]['end']-e['start']<=3 for e in events))
        self.assertEqual(sum(len(e['words']) for e in events),6)

    def test_manual_phrase_and_position_boundaries(self):
        raw=transcript([('Carlo',0,.2),('Gino',.21,.4),('says',.41,.6),('hello',.61,.8)],1)
        raw['words'][1]['break_after']=True
        raw['words'][3]['center_y_fraction']=.2
        events=caption_events(raw,STYLE)
        self.assertEqual([e['text'] for e in events],['Carlo Gino','says','hello'])
        self.assertEqual(events[-1]['center_y_fraction'],.2)

    def test_break_before_and_source_change(self):
        raw=transcript([('A',0,.2),('B',.21,.4),('C',.41,.6)],1)
        raw['words'][1]['break_before']=True
        raw['words'][2]['source']='second.mov'
        self.assertEqual(len(caption_events(raw,STYLE)),3)

    def test_character_limit_and_long_word_review(self):
        raw=transcript([('abcdefghij',i*.2,i*.2+.15) for i in range(6)],2)
        self.assertEqual([len(e['words']) for e in caption_events(raw,STYLE)],[5,1])
        long_word='a'*80
        event=caption_events(transcript([(long_word,0,.5)],1),STYLE)[0]
        self.assertEqual(event['text'],long_word)
        self.assertTrue(event['layout_review_required'])

    def test_caption_rejects_overlapping_word_intervals(self):
        with self.assertRaises(ValueError):
            caption_events(transcript([('A',.1,.6),('B',.5,.8)],1),STYLE)

    def test_empty_transcript_has_no_captions(self):
        self.assertEqual(caption_events(transcript([],2),STYLE),[])


    def test_caption_rejects_sentence_timestamp(self):
        with self.assertRaises(ValueError):
            caption_events(transcript([('hello world',0,1)],2),STYLE)

    def test_caption_rejects_shared_onset(self):
        with self.assertRaises(ValueError):
            caption_events(transcript([('A',.2,.2),('B',.2,.5)],1),STYLE)

    def test_settings_match_user_brief(self):
        self.assertEqual((STYLE['format']['width'],STYLE['format']['height']),(1080,1920))
        self.assertFalse(STYLE['sound']['music'])
        self.assertFalse(STYLE['sound']['pop_every_caption_word'])
        self.assertFalse(STYLE['delivery']['publish_automatically'])
        self.assertEqual(STYLE['captions']['mode'],'phrase_chunks')
        self.assertEqual(STYLE['captions']['max_lines'],2)
        self.assertEqual(STYLE['branding']['palette']['background'],'#102B2D')
        self.assertEqual(STYLE['branding']['palette']['accent'],'#EFA269')
        self.assertEqual(STYLE['branding']['website'],'carlogino.com')
        self.assertEqual(STYLE['branding']['handle'],'@codegino')
        self.assertTrue(STYLE['graphics']['spoken_effects_are_brief'])
        self.assertTrue(STYLE['verification']['video_only_frame_hashes'])

    def test_generated_effects_are_short_and_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            make(temp)
            for filename in ['whoosh.wav','pop.wav']:
                with wave.open(str(Path(temp)/filename)) as wav:
                    self.assertEqual(wav.getframerate(),48000)
                    self.assertGreater(wav.getnframes(),0)
                    self.assertLess(wav.getnframes()/wav.getframerate(),.3)

if __name__=='__main__':
    unittest.main()
