import numpy as np

GENDER_MAP = {
    "male": 0,
    "female": 1,
    "non-binary": 2
}

MEDICAL_CONDITIONS = [
    'diabetes', 'asthma', 'heart condition', 'depression', 'schizophrenia',
    'arthritis', 'vision loss', 'hypertension', 'bipolar disorder', 'ptsd',
    'anxiety disorder', 'alcohol addiction', 'drug addiction', 'tubercolosis',
    'cancer', 'hiv/aids', 'hepatitis c', 'epilepsy', 'back pain',
    'skin infection', 'open wounds', 'malnutrition', 'anemia',
    'respitory infections', 'hearing loss', 'sleep disorders', 'heart disease',
    'copd', 'obesity', 'stroke recovery', 'immune deficiency', 'paranoia',
    'psychosis', 'autism', 'ulcers', 'kidney failure', 'fatigue', 'mrsa',
    'lupus', 'parkinson'
]

PROBLEMS_CONCERNS = [
    'lost job', 'evicted', 'family conflict', 'mental health', 'shelter hopping',
    'financial loss', 'danger to self', 'ignored', 'low funds', 'orphaned',
    'unemployed', 'suicidal', 'social isolation', 'substance abuse', 'hungry',
    'thirsty', 'police harassment', 'gang violence', 'unsafe neighborhoods',
    'discrimination', 'lack of ID', 'trust issues', 'lack of childcare',
    'sexual assault', 'trauma', 'fear of deportation', 'gambling addict',
    'peer pressure', 'rejection from shelters', 'illiteracy', 'no phone or comms',
    'prior incarceration', 'no access to legal help', 'natural disaster survivor',
    'robbery', 'panic attacks', 'bullying', 'lack of hygiene'
]

def multi_hot_encode(values, reference_list):
    """
    Encodes list of strings into binary vector based on reference list.
    """
    return [1 if ref in values else 0 for ref in reference_list]

def prepare_features_for_prediction(structured_info):
    """
    Converts structured info dictionary into a numerical feature vector.
    """
    age = int(structured_info.get("age", 0))
    gender_str = structured_info.get("gender", "").lower()
    gender = GENDER_MAP.get(gender_str, 0)

    med_conditions = structured_info.get("medical_conditions", "").lower().split("|")
    med_encoded = multi_hot_encode(med_conditions, MEDICAL_CONDITIONS)

    problems = structured_info.get("problems_concerns", "").lower().split("|")
    prob_encoded = multi_hot_encode(problems, PROBLEMS_CONCERNS)

    location_known = int(structured_info.get("location_known", 0))
    family_mentioned = int(structured_info.get("family_mentioned", 0))

    return [age, gender] + med_encoded + prob_encoded + [location_known, family_mentioned]
