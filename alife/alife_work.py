from globals import *

import life as lfe

import judgement
import combat
import speech
import brain
import jobs

import logging

STATE = 'working'
ENTRY_SCORE = -1

def conditions(life, alife_seen, alife_not_seen, targets_seen, targets_not_seen, source_map):
	RETURN_VALUE = STATE_UNCHANGED

	if not judgement.is_safe(life):
		return False

	if life['state'] in ['combat', 'searching', 'hiding', 'hidden', 'needs', 'looting']:
		return False

	if not life['job'] and not jobs.alife_is_factor_of_any_job(life):
		return False
	
	if not life['state'] == STATE:
		RETURN_VALUE = STATE_CHANGE

	return RETURN_VALUE

def tick(life, alife_seen, alife_not_seen, targets_seen, targets_not_seen, source_map):
	if jobs.alife_is_factor_of_any_job(life):
		lfe.clear_actions(life)
		return True
	
	if life['task'] and life['task']['callback'](life):
		jobs.complete_task(life)
