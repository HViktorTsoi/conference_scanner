# pip install openai
import os, openai
import bibtexparser
import tqdm
from bibtexparser.bwriter import BibTexWriter
import json

prompt_template = """
You are a senior researcher in Embodied AI and healthcare-related mobile computing. From the BibTeX I will provide, according to the titles, abstracts and keywords, identify papers relevant to the following two topics:

- Broadly defined robot systems 
    (including embodied AI, robot navigation, robotic grasping, robotic manipulation, autonomous driving, drone systems, LiDAR / radar / event camera / depth camera sensing, perception, SLAM, planning, control, telepresence/teleoperation, etc.)
- Broadly defined systems for health care 
    (including medical/clinical systems, public health, wellness monitoring, hand hygiene, assistive devices, daily life monitoring, mental health, cardio health, HAR, etc.)
Return ONLY valid JSON with this exact structure:
{
"Broadly defined robot systems": [
{ "title": "...", "doi": "..." },
...
],
"Broadly defined systems for health care": [
{ "title": "...", "doi": "..." },
...
]
}

Requirements:

- Use the DOI in the BibTeX. If only a URL is provided, use that URL as the doi value.
- Do not include any fields other than title and doi.
- If a category has no matching papers, return an empty array for that category.
- Do not add explanations or comments outside the JSON.

Here is the BibTeX:
----------------------------------

"""


def process_bibtex_file(bibtex_name, batch_size):
    """
    Process a BibTeX file, generate prompts, and call the OpenAI API.

    Args:
        bibtex_name (str): Path to the BibTeX file.
        batch_size (int): Number of entries per batch.
    """
    bib = bibtexparser.load(open(bibtex_name, 'r', encoding='utf-8'))

    # Split entries into batches
    bib_batches = [bib.entries[i:i + batch_size]
                   for i in range(0, len(bib.entries), batch_size)]

    # Convert each batch to BibTeX string
    writer = BibTexWriter()
    prompts = []
    for batch in bib_batches:
        database_batch = bibtexparser.bibdatabase.BibDatabase()
        database_batch.entries = batch
        batch_bibtex = writer.write(database_batch)
        prompt = prompt_template + batch_bibtex + "\n----------------------------------\n"
        prompts.append(prompt)

    client = openai.OpenAI(
        # api_key=os.environ['POE_API_KEY'],  # https://poe.com/api_key
        api_key=open('POE_API_KEY').read(),  # https://poe.com/api_key
        base_url="https://api.poe.com/v1",
    )

    result = []
    # Call API for each prompt
    for prompt in tqdm.tqdm(prompts):
        chat = client.chat.completions.create(
            model="GPT-5",  # or other models (Claude-Sonnet-4, Gemini-2.5-Pro, Llama-3.1-405B, Grok-4..)
            messages=[{
                "role": "user",
                "content": prompt
            }],
        )
        # print(chat.choices[0].message.content)
        print('Total tokens', chat.usage.total_tokens)
        response = json.loads(chat.choices[0].message.content)  # Validate JSON
        print(len(response))
        result.append(response)

        # Save result to JSON file
        output_dir = './output/agent/'
        output_file = os.path.join(output_dir, f'{os.path.basename(bibtex_name)}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4)


if __name__ == '__main__':
    # Traverse the bibtex directory and process files containing "MobiCom"
    bibtex_dir = './bibtex'
    # target_keyword = "MobiCom"
    # target_keyword = "MobiSys"
    # target_keyword = "SenSys"
    target_keyword = "IPSN"

    for file in reversed(sorted(os.listdir(bibtex_dir))):
        if file.lower().endswith('.bib') and target_keyword.lower() in file.lower():
            bibtex_path = os.path.join(bibtex_dir, file)
            print(bibtex_path)
            process_bibtex_file(bibtex_path, batch_size=10)
