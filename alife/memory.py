from globals import *

import life as lfe

import logging

def process_questions(life):
	for question in lfe.get_questions(life):
		
		#if not question['text'] in QUESTIONS_ANSWERS:
		#	logging.error('%s not in QUESTIONS_ANSWERS' % question['text'])
		#	continue
		
		#_answered = False
		#for memory in lfe.get_memory(life, matches=QUESTIONS_ANSWERS[question['text']]):
		#	if not memory['id'] in question['answered']:
		#		question['answered'].append(memory['id'])
		#		_answered = True
		
		print question['text']
		if question['answer_callback'](life, question['answer_match']):
			question['answered'].append(memory['id'])
			_answered = True
		
		#if _answered:
		#	if len(question['answered']) == 1:
		#		logging.debug('%s answered question: %s' % (' '.join(life['name']), memory['text']))
		#	else:
		#		logging.debug('%s added more detail to question: %s' % (' '.join(life['name']), memory['text']))

def detect_lies(life):
	#for memory in life['memories']:
	for question in lfe.get_questions(life, no_filter=True):
		if not question['text'] in QUESTIONS_ANSWERS:
			logging.error('%s not in QUESTIONS_ANSWERS' % question['text'])
			continue
		
		for answer in [get_memory_via_id(life, a) for a in question['answered']]:
			print answer.keys()
		
def process(life):
	process_questions(life)
	detect_lies(life)