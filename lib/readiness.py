from __future__ import annotations

from typing import Dict, Tuple

# Minimal readiness model ported for in-dashboard use

LAND_OPTIONS = [
    ('i_have_not_decided_on_the_location_yet', "Haven't decided location"),
    ('i_need_to_buy_the_land', 'Need to buy land'),
    ('i_have_not_started_any_site_prep_yet', 'No site prep yet'),
    ('i_need_to_grade_the_land', 'Need to grade land'),
    ('i_need_to_pour_concrete_or_gravel', 'Need to pour base (concrete/gravel)'),
    ('i_dont_know', "I don't know"),
]
SITE_READY_OPTIONS = [
    ('site_is_ready', 'Site is ready'),
    ('i_dont_need_foundation', "Don't need foundation"),
    ('i_dont_know', "I don't know"),
]
PERMIT_OPTIONS = [
    ("i_don't_need_permits_on_my_land", "Don't need permits"),
    ('i_need_help_with_permits', 'Need help with permits'),
    ('i_need_to_look_into_permits', 'Need to look into permits'),
    ('i_already_have_my_permits', 'Already have permits'),
    ('i_dont_know', "I don't know"),
]
LICENSE_OPTIONS = [
    ('contractors_license_require', "Contractor's license required"),
    ('i_dont_need_contractors_license', "Don't need contractor's license"),
    ('i_dont_know', "I don't know"),
]
DRAWINGS_OPTIONS = [
    ('i_need_site_specific_drawings', 'Need site-specific drawings'),
    ('i_dont_need_site_specific_drawings', "Don't need site-specific drawings"),
    ('i_dont_know', "I don't know"),
]
FINANCING_OPTIONS = [
    ('i_require_financing', 'Require financing'),
    ('i_dont_need_financing', "Don't need financing"),
    ('maybe', 'Maybe / not sure'),
    ('i_dont_know', "I don't know"),
]
FINCO_OPTIONS = [
    ('i_have_my_own_financing_company', 'I have my own financing company'),
    ('i_dont_have_a_financing_company_yet', "I don't have a financing company yet"),
    ('i_dont_know', "I don't know"),
]
SCHEDULE_OPTIONS = [
    ('asap', 'ASAP'),
    ('2-4_weeks', '2–4 weeks'),
    ('4-8_weeks', '4–8 weeks'),
    ('2-3_months', '2–3 months'),
    ('3+_months', '3+ months'),
    ('i_dont_know', "I don't know"),
]

QUESTION_COLUMNS = [
    'land_status','site_ready','permit_status','license_status','drawings_status',
    'financing_status','financing_company','install_timeframe'
]

SCORES = {
    'land_status': {
        'i_have_not_decided_on_the_location_yet': 0.0,
        'i_need_to_buy_the_land': 0.0,
        'i_have_not_started_any_site_prep_yet': 0.0,
        'i_need_to_grade_the_land': 0.5,
        'i_need_to_pour_concrete_or_gravel': 0.5,
        'i_dont_know': 0.0,
    },
    'site_ready': {
        'site_is_ready': 3.0,
        'i_dont_need_foundation': 2.0,
        'i_dont_know': 0.0,
    },
    'permit_status': {
        "i_don't_need_permits_on_my_land": 2.0,
        'i_need_help_with_permits': 0.0,
        'i_need_to_look_into_permits': 0.0,
        'i_already_have_my_permits': 2.0,
        'i_dont_know': 0.0,
    },
    'license_status': {
        'contractors_license_require': 0.0,
        'i_dont_need_contractors_license': 1.0,
        'i_dont_know': 0.0,
    },
    'drawings_status': {
        'i_need_site_specific_drawings': 0.0,
        'i_dont_need_site_specific_drawings': 1.0,
        'i_dont_know': 0.0,
    },
    'financing_status': {
        'i_require_financing': 0.0,
        'i_dont_need_financing': 1.0,
        'maybe': 0.0,
        'i_dont_know': 0.0,
    },
    'financing_company': {
        'i_have_my_own_financing_company': 0.5,
        'i_dont_have_a_financing_company_yet': 0.0,
        'i_dont_know': 0.0,
    },
    'install_timeframe': {
        'asap': 3.0,
        '2-4_weeks': 2.5,
        '4-8_weeks': 2.0,
        '2-3_months': 1.0,
        '3+_months': 0.5,
        'i_dont_know': 0.0,
    },
}


def score_row(answers: Dict[str, str]) -> float:
    land_points = SCORES['land_status'].get(answers.get('land_status', 'i_dont_know'), 0.0)
    site_points = SCORES['site_ready'].get(answers.get('site_ready', 'i_dont_know'), 0.0)
    if answers.get('site_ready') in ('site_is_ready', 'i_dont_need_foundation'):
        land_points = 0.0
    permit_points = SCORES['permit_status'].get(answers.get('permit_status', 'i_dont_know'), 0.0)
    license_points = SCORES['license_status'].get(answers.get('license_status', 'i_dont_know'), 0.0)
    drawings_points = SCORES['drawings_status'].get(answers.get('drawings_status', 'i_dont_know'), 0.0)
    financing_points = SCORES['financing_status'].get(answers.get('financing_status', 'i_dont_know'), 0.0)
    finco_points = 0.0
    if answers.get('financing_status') == 'i_require_financing':
        finco_points = SCORES['financing_company'].get(answers.get('financing_company', 'i_dont_know'), 0.0)
    schedule_points = SCORES['install_timeframe'].get(answers.get('install_timeframe', 'i_dont_know'), 0.0)
    total = land_points + site_points + permit_points + license_points + drawings_points + financing_points + finco_points + schedule_points
    return round(float(total), 2)


def assign_level(score: float) -> str:
    if score < 2.5:
        return 'Level 1'
    if score < 5.0:
        return 'Level 2'
    if score < 9.0:
        return 'Level 3'
    return 'Level 4'


def compute(answers: Dict[str, str]) -> Tuple[float, str]:
    s = score_row(answers)
    return s, assign_level(s)
