import base64
import requests
import json
import glob
from tinydb import TinyDB, Query
from collections import defaultdict
import logging
import re

OLLAMA_API_URL = "http://10.0.0.20:11434/api/generate"

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def get_encoded_image(image_path):
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def prompt_multimodal(prompt, images):
    data = {
        "model": f"llava:13b",
        "stream": False,
        "prompt": prompt,
        "images": images,
        "options": {
            "temperature": 0,
        }
    }
    response = requests.post(OLLAMA_API_URL, data=json.dumps(data))
    return response.json()['response']

def prompt_llm(prompt):
    data = {
        "model": "miqu:70b_q4_k_m",
        "stream": False,
        "prompt": prompt,
        "options": {
            "temperature": 0
        }
    }
    response = requests.post(OLLAMA_API_URL, data=json.dumps(data))
    return response.json()['response']

def image_analysis_prompt(attribute):
    return f"Here are two images, one is a reference image taken from lunar surface and the other is an image rendered from a 3D model to simulate the lunar surface. Provide details of the similarities and differences of these images based on {attribute}?"

def analysis_score_prompt(analysis):
    return f"```\n{analysis}\n```\nThis is an analysis of similarities between a reference image of the lunar surface and a 3D model rendering. Given this analysis, return a score from 0.0 to 1.0 for how similar the 3D model rendering is to the reference lunar surface image with regard to topography. Do not give an explanation for your score. Only respond with a number between 0.0 and 1.0."

reference_image_path = 'reference.png'
attributes = ['ridge and valley formations', 'mare and highland areas', 'scale and perspective']
render_directory = 'renders'

db = TinyDB(f'{render_directory}/db.json')

for image_path in glob.glob(render_directory + '/**/*.png', recursive=True):
    new_record = {
        'image_path': image_path,
        'model': image_path.split('/')[1],
        'analyses': [],
        'scores': []
    }
    if not db.contains(Query().image_path == new_record['image_path']):
        logging.info(f"adding {image_path} to db")
        db.insert(new_record)

unanalysed_images = db.search(Query().analyses == [])
for unanalysed_image in unanalysed_images:
    analyses = []
    for attribute in attributes:
        logging.info(f"analysing `{unanalysed_image['image_path']}` for `{attribute}` attribute")
        analysis_prompt = image_analysis_prompt(attribute)
        analyses.append(prompt_multimodal(analysis_prompt, [get_encoded_image(reference_image_path), get_encoded_image(unanalysed_image['image_path'])]))
    db.update({'analyses': analyses}, Query().image_path == unanalysed_image['image_path'])

number_extract_pattern = r'\d+\.\d+'
unscored_images = db.search((Query().analyses != []) & (Query().scores == []))
for unscored_image in unscored_images:
    logging.info(f"scoring {len(unscored_image['analyses'])} analyses for `{unscored_image['image_path']}`")
    scores = []
    try:
        for analysis in unscored_image['analyses']:
            score_prompt = analysis_score_prompt(analysis)
            response = prompt_llm(score_prompt)
            match = re.search(number_extract_pattern, response.replace('3D', ''))
            scores.append(float(match.group()))
        db.update({'scores': scores}, Query().image_path == unscored_image['image_path'])
    except AttributeError:
        logging.info(f"bad response for {unscored_image['image_path']}")
        # Ignore the AttributeError caused when response does not contain number and continue execution of subsequent images
        pass


processed_images = db.search(Query().scores != [])

grouped_data = defaultdict(list)
for record in processed_images:
    grouped_data[record['model']].append(record)

average_scores = {}
for model, records in grouped_data.items():
    total_scores = sum(float(score) for record in records for score in record['scores'])
    num_scores = sum(len(record['scores']) for record in records)
    average_scores[model] = total_scores / num_scores

# Print results
print("Average scores by model:")
for model, avg_score in average_scores.items():
    print(f"{model}: {round(avg_score, 3)}")
