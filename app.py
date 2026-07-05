from flask import Flask, request, jsonify, render_template
import json
import requests
from parsing_functions import *
import jp_errant
import re
import ltp
import random
from API_Config import *

# -----------------------------------------------------------------------------------------------------------------

app = Flask(__name__)

# *****************************************************************************************************************
# Web HTTP
@app.route('/')
def index():
    return render_template('webpage.html', content="")

@app.route('/data', methods=['POST'])
def get_data():
    data = request.get_json()
    passage = data.get('input_data')
    
    anno_html = "<p><div class='sentence'>"
    corr_html = "<p><div class='sentence'>"

    orig_sentences, max_len = split_into_sentences(passage)
    corrected_sens = gen_corrections(orig_sentences, max_len)

    for orig, cors in zip(orig_sentences, corrected_sens):
        cur_og_html, cur_anno_html, cur_corr_html = generate_errant_html(orig, cors, 'zh', tagless_mode_setting=True)
        anno_html += cur_anno_html
        corr_html += cur_corr_html

    anno_html += "</div></p>"
    corr_html += "</div></p>"

    response_data = {'sen': passage,'anno': anno_html, 'corr': corr_html}
    return jsonify(response_data)

# ***************************************************************************************************************** 
# Mobile HTTP 

@app.route('/dataMobile', methods=['POST'])
def get_sentence():
    data = request.get_json()
    langIn = data.get('langIn')
    langOut = data.get('langOut')

    l0 = random.randint(1, 20)
    sen_id = random.randrange(0, 7099, 2)
    f = open(f"trimmed_questions/corpus_{l0}.txt", "r", encoding="utf8")
    lines=f.readlines()

    # sen_a is English, sen_b is Chinese
    sen_a = lines[sen_id]
    sen_b = lines[sen_id + 1]
    f.close()

    if PRINT:
        print(l0, sen_id, sen_a, sen_b, langIn, langOut)

    # hard code lang selection for now
    prompt = sen_a if langIn == "en" else sen_b
    answer = sen_b if langIn == "en" else sen_a

    return jsonify({'message': json.dumps({"prompt": prompt, "answer": answer})})


@app.route('/resultMobile', methods=['POST'])
def result():
    data = request.get_json()
    input = data.get('input')
    langIn = data.get('langIn')
    langOut = data.get('langOut')
    prompt = data.get('prompt')
    answer = data.get('answer')
    
    orig = input
    cors = answer

    if PRINT:
        print(input, answer)

    try:
        og_html, anno_html, corr_html = generate_errant_html(orig, cors, langOut, tagless_mode_setting=False)
    except:
        print("Bad input from front end.")
        return {'error': 'Invalid message'}, 400  

    # html templates
    html = f"""
    <div>
        <div style="display:flex; flex-direction:row;">
            {anno_html}
        </div>
    </div>    
    """

    html_corr = f"""
    <div>
        <div style="display:flex; flex-direction:row;">
            {corr_html}
        </div>
    </div>    
    """
    feedback = "Network Error"
    feedback = """<div class='sentence'>""" + llm_feedback(input, answer, langOut) + "</div>"

    return jsonify({'message': json.dumps({"og": prompt,"input": input, "anno": html, "corr": html_corr, "langIn": langIn, "langOut": langOut, "feedback": feedback})}), 200    


# -----------------------------------------------------------------------------------------------------------------
# This code is modified from parallel_to_m2.py file in jp-errant
def gen_errant(orig_sen, cors_sen, lang, args:dict, nlp=None):

    result = ""
    
    # Process an arbitrary number of files line by line simultaneously. Python 3.3+
    # See https://tinyurl.com/y4cj4gth . Also opens the output m2 file.
    orig = orig_sen
    cors = [cors_sen]
    
    # Parse orig with Stanza
    orig = annotators[lang].parse(orig.strip())

    # Skip the line if orig is empty
    if not orig: return result

    # Write orig to the output m2 file
    # Putting spaces between words
    s_text = " ".join([token.text 
                       for token in orig.iter_words()
                      ])
    result += "S " + s_text + "\n"
    # out_m2.write("S " + orig.text +"\n")
    # Loop through the corrected texts
    for cor_id, cor in enumerate(cors):
        # If the texts are the same, write a noop edit
        if orig.text.replace(" ", "").strip() == cor.replace(" ", "").strip():
            result += noop_edit(cor_id)+"\n"
        # Otherwise, do extra processing
        else:
            # Parse cor with Stanza
            cor = annotators[lang].parse(cor.strip())
            # Align the texts and extract and classify the edits
            edits = annotators[lang].annotate(orig, cor, args["lev"], args["merge"])
            # Loop through the edits
            for edit in edits:
                # Write the edit to the output m2 file
                result += edit.to_m2(cor_id)+"\n"
    # Write a newline when we have processed all corrections for each line
    result += "\n"

    return result

# Input: A coder id
# Output: A noop edit; i.e. text contains no edits
def noop_edit(id=0):
    return "A -1 -1|||noop|||-NONE-|||REQUIRED|||-NONE-|||"+str(id)
# -----------------------------------------------------------------------------------------------------------------

def generate_errant_html(orig, cors, lang, tagless_mode_setting=False):
    result = gen_errant(orig_sen=orig, cors_sen=cors, lang=lang, args=args)
    result_split = result.splitlines()
    converted_res = m2_to_sentences(result_split)
    sen_obj = converted_res[0]
    og_html, anno_html, corr_html = sentence_to_html(sen_obj, tagless_mode=tagless_mode_setting)

    return og_html, anno_html, corr_html

def split_into_sentences(passage):
    # return [passage], len(passage)
    # regex modified from https://github.com/tsroten/zhon/blob/main/src/zhon/hanzi.py

    #: A string of Chinese stops.
    # added some English punctuation just in case (of typos)
    stops = (
        "\uFF0E"  # Fullwidth full stop
        "\uFF01"  # Fullwidth exclamation mark
        "\uFF1F"  # Fullwidth question mark
        "\uFF61"  # Halfwidth ideographic full stop
        "\u3002"  # Ideographic full stop
        "."
        "!"
        "?"
    )

    # container-closing marks (e.g. quotation or brackets).
    _sentence_end = r"[{stops}][」﹂”』’》）］｝〕〗〙〛〉】\u007D \'\"\]\)]*".format(stops=stops)

    # split passage into sentences
    re_split = re.compile("({})".format(_sentence_end))
    sentences = re_split.split(passage)

    if PRINT:
        print(sentences)

    if sentences[0] == passage: return [passage], len(passage)

    list_sentence = []
    max_len = 0
    for i in range(0, len(sentences), 2):
        if i + 1 < len(sentences) - 1:
            sen = sentences[i].strip() + sentences[i + 1].strip()
            list_sentence.append(sen)
            max_len = max(max_len, len(sen))

    if PRINT:
        for i, sen in enumerate(list_sentence):
            print(f"Sentence {i + 1}: {sen}")

    return list_sentence, max_len

def seg_sentences(sentences):
    ltp_model = ltp.LTP()

    segmented_sens = []
    S1 = []

    for sentence in sentences:
        # Use LTP for word segmentation
        seg_result = ltp_model.pipeline([sentence], tasks=["cws"])
        # Extract the segmented words (cws = Chinese Word Segmentation)
        segmented_words = seg_result.cws[0]
        segmented_sens.append(segmented_words)

        # Add the space-separated sentence to the new list
        S1.append(' '.join(segmented_words))

    if PRINT:
        print("Segmented sentences using LTP:")
        for i, segmented in enumerate(segmented_sens, start=1):
            print(f"{' '.join(segmented)}")

    return S1

def gen_corrections(sentences, max_len):

    corrected_sens = []
    T1 = []
    S1 = seg_sentences(sentences)
    model_temperature = 0.000001

    for sentence in S1:
        # Prepare the prompt for grammar correction
        prompt = f"以下句子是经过分词处理的结构化输入。请在此基础上改正语法错误，并尽量最小化修改。输出时请将修改后的句子以正常语句格式（不含分词）呈现，不要输出其他信息。句子如下：{sentence}"

        # LLM API
        data=json.dumps({
            "model": api_config["model"],
            "messages": [
            {
                "role": "user",
                "content": prompt
            }
            ],
            'temperature': model_temperature
        })

        try:
            # Send request to LLM
            response = requests.post(
                url = api_config['url'],
                headers={
                    "Authorization": api_config['key'],
                    "Content-Type": "application/json",
                    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional.
                    "X-Title": "<YOUR_SITE_NAME>", # Optional.
                },
                data=data
            )
            response_json = response.json()

            # Extract the corrected sentence from response
            corrected_sen = response_json['choices'][0]['message']['content'].strip()
            corrected_sens.append(corrected_sen)
            T1.append(corrected_sen)

            if PRINT:
                print(f"Original : {sentence}")
                print(f"Corrected: {corrected_sen}")
                print("-" * 50)     
        except Exception as e:
            print(f"Error processing sentence: {e}")
            corrected_sens.append(sentence + " API ERROR.")  # Keep original if error occurs
            T1.append(sentence)  # Also add to T0 for consistency

    return corrected_sens

def llm_feedback(og_sen, corr_sen, lang):
    if lang == "en":
        prompt = f"Given the original sentence and the corrected sentence, please analyze mistakes such as grammatical or word choice errors made in the original sentence, and provide English language learning suggestions based on the errors made. Ensure that the language of the output text is Chinese. Do not output a item-by-item analysis. The output should be a summarized analysis feedback of around two to three sentences. Do not include any other content. Original sentence: {og_sen} Corrected sentence: {corr_sen}"
    else:
        prompt = f"给与原始语句和纠错改正后语句，请分析原始语句中语法与用词等错误，并根据错误原因提供中文语言学习建议。确保输出语言为英文语句。不必输出单条问题分析，仅需输出简短约二到三句话的反馈总结，不要输出其他信息。原始语句：{og_sen} 纠错改正后语句：{corr_sen}"

    model_temperature = 0.000001

    data=json.dumps({
        "model": api_config["model"],
        "messages": [
        {
            "role": "user",
            "content": prompt
        }
        ],
        'temperature': model_temperature
    })

    # Send request to LLM
    response = requests.post(
        url = api_config['url'],
        headers={
            "Authorization": api_config['key'],
            "Content-Type": "application/json",
            "HTTP-Referer": "<YOUR_SITE_URL>", # Optional.
            "X-Title": "<YOUR_SITE_NAME>", # Optional.
        },
        data=data
    )
    
    feedback = "API Down. Try again later."

    try:
        response_json = response.json()
        feedback = response_json['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error: {e} {feedback}")
        
    return feedback

# -----------------------------------------------------------------------------------------------------------------

# loading now done by jp-errant
args = {
    "lev": True,
    "merge": "rules"
}

annotators = {
    'zh': jp_errant.load('zh', legacy=True),
    'en': jp_errant.load('en', legacy=True)
}

# some env variables
# CUDA = False
PRINT = False

# if CUDA:
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model = model.to(device)  # explicitly move the model to the GPU

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)