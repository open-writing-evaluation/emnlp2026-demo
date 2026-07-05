# code from 08_visualization_with_WB_corrections.ipynb by github.com/minhngca
'''************************************************************************************************************************************'''
def m2_to_sentences(lines:list[str]) -> list:
    """ Convert m2 file lines into sentences """
    output = []
    sentence = ""
    edits = []
    # start_of_batch = False # a batch is a group of annotations of the same sentence, by different models

    for line in lines:
        # if line.startswith("index:"):
        #     sentence_id = line.split()[-1]
        #     start_of_batch = True 
        if line.startswith("S"):
            # if not start_of_batch:
            #     # append previous sentence 
            #     # output.append({"sentence_id": sentence_id, "model_name": model_name, "S":sentence, "A":edits})
            # else:
            #     # the first sentence of batch -> not saving the previous sentence
            #     start_of_batch = False 
                
            # New sentence
            # model_name = line.split(":")[0][2:].strip("_")  # Sentence annotated with model name )S_LTP___, S_Spacy_, S_Stanza)
            sentence = line[2:].strip() # Skip the "S " beginning
            edits = [] 
        elif line.startswith("A"):
            # Annotation line
            edits.append(line[2:]) # Skip the "A " beginning
        elif line == "":
            # End of sentence -> add to output
            # output.append({"sentence_id": sentence_id, "model_name": model_name, "S":sentence, "A":edits})
            output.append({"S":sentence, "A":edits})
        
    return output 

def parse_edit_string(sentence: str, edit_str:str) -> dict:
    """ Parse edit string to JSON object """
    result = dict()
    tokens = edit_str.split("|||")
    result["o_start"] = int(tokens[0].split()[0])
    result["o_end"] = int(tokens[0].split()[1])
    result["type"] = tokens[1]
    result["o_str"] = " ".join(sentence.split()[result["o_start"]:result["o_end"]])
    result["c_str"] = tokens[2]
    result["annotator_id"] = int(tokens[-1])
    
    return result 

def flatten(l):
    return [item for sublist in l for item in sublist]

'''************************************************************************************************************************************'''
# define some constants for HTML render
# modified from code by github.com/minhngca
# changed html for different styling
HTML_TAGS = {
    "insert_start": "<span class='green_highlight'>",
    "insert_end": "</span>",
    "remove_start": "<span class='red_highlight'>",
    "remove_end": "</span>",
}

HTML_TAGS_WB = {
    "insert_start": "<span class='darkgreen_highlight'>",
    "insert_end": "</span>",
    "remove_start": "<span class='darkred_highlight'>",
    "remove_end": "</span>",
}

# modified from code by github.com/minhngca
# changed the generated html for different styling
# for a given sentence, return the html of the original sentence, the html of all of the annotations, and the html of all of the corrections
def annotations_to_html(sentence_object: dict, verbose:bool=False):
    """ Visualize edits of a sentence and annotations, return HTML string """
    og_html = ""
    anno_htmls = []
    corr_htmls = []
    anno_corr_htmls = []

    sentence = sentence_object["S"]
    og_html = f"<p><div class='sentence'>{sentence}</div></p>"
    
    if verbose: print("S =", sentence)
    
    # result.append(f"<b>Corrections:</b><br>")
    
    current_annotator_id = 0
    current_output_html_str = ""
    current_output_tokens = sentence.split()            # tokens for annotated (+ X) (- X) HTML
    current_corrected_output_tokens = sentence.split()  # tokens for corrected text HTML
    
    for edit_id, edit_str in enumerate(sentence_object["A"]):
        if verbose: print("Edit =", edit_str)
        edit_obj = parse_edit_string(edit_str=edit_str, sentence=sentence)
        if verbose: print("Edit object =", edit_obj)
        
        if edit_obj.get("annotator_id") != current_annotator_id:
            # add current html string to the output
            current_corrected_output_html_str = f"<p><div class='sentence'>{' '.join(current_corrected_output_tokens)}</div></p>"
            current_output_html_str = f"<p><div class='sentence'>{' '.join(current_output_tokens)}</div></p>"

            # store current sentence html
            anno_htmls.append(current_output_html_str)
            corr_htmls.append(current_corrected_output_html_str)
                        
            # reset current html string
            current_output_html_str = ""
            current_output_html_str = ""
            current_output_tokens = sentence.split()
            current_corrected_output_tokens = sentence.split()
            
            current_annotator_id = edit_obj.get("annotator_id")
            if verbose: print("New annotator detected:", current_annotator_id)

        HTML_tags = HTML_TAGS_WB
        
        if edit_obj.get("type").startswith("M:"): # Missing
            if edit_obj.get("o_start") < len(current_output_tokens):
                current_output_tokens[edit_obj.get("o_start")] =(f"{HTML_tags.get('insert_start')} {edit_obj.get('c_str')}{HTML_tags.get('insert_end')} " + 
                                                                  current_output_tokens[edit_obj.get("o_start")]
                                                                 )

                # modify corrected text
                current_corrected_output_tokens[edit_obj.get("o_start")] =(f"<b>{edit_obj.get('c_str')}</b> " + 
                                                                           current_corrected_output_tokens[edit_obj.get("o_start")]
                                                                          )
            else: 
                # add something at the end of the sentence
                current_output_tokens.append(f"{HTML_tags.get('insert_start')} {edit_obj.get('c_str')}{HTML_tags.get('insert_end')} ")

                # modify corrected text
                current_corrected_output_tokens.append(f"<b>{edit_obj.get('c_str')}</b>")
            
            pass
        elif edit_obj.get("type").startswith("U:"): # Unnecessary
            current_output_tokens[edit_obj.get("o_start")] = (f"{HTML_tags.get('remove_start')} " + 
                                                              current_output_tokens[edit_obj.get("o_start")]
                                                             )
            current_output_tokens[edit_obj.get("o_end")-1] += HTML_tags.get('remove_end')

            # modify corrected text
            for token_id in range(edit_obj.get("o_start"), edit_obj.get("o_end")):
                # clear all unnecessary tokens
                current_corrected_output_tokens[token_id] = ""
                
        elif edit_obj.get("type").startswith("R:"): # Replacement
            current_output_tokens[edit_obj.get("o_start")] = (f"{HTML_tags.get('remove_start')} " + 
                                                              current_output_tokens[edit_obj.get("o_start")]
                                                             )
            current_output_tokens[edit_obj.get("o_end")-1] += (HTML_tags.get('remove_end') + 
                                                              f" {HTML_tags.get('insert_start')} {edit_obj.get('c_str')}{HTML_tags.get('insert_end')}"
                                                              )
                                                             
            # modify corrected text
            for token_id in range(edit_obj.get("o_start"), edit_obj.get("o_end")):
                # clear all unnecessary tokens
                current_corrected_output_tokens[token_id] = ""
    
            # add new corrected text
            current_corrected_output_tokens[edit_obj.get("o_start")] = f"<b>{edit_obj.get('c_str')}</b>"
    
    # add last html result to the output
    current_corrected_output_html_str = f"<p><div class='sentence'>{' '.join(current_corrected_output_tokens)}</div></p>"
    current_output_html_str = f"<p><div class='sentence'>{' '.join(current_output_tokens)}</div></p>"

    # store current sentence html
    anno_htmls.append(current_output_html_str)
    corr_htmls.append(current_corrected_output_html_str)

    return og_html, anno_htmls, corr_htmls


def annotations_to_html(sentence_object: dict, verbose:bool=False, sen_tag=True):
    """ Visualize edits of a sentence and annotations, return HTML string """
    og_html = ""
    anno_htmls = []
    corr_htmls = []
    anno_corr_htmls = []

    sentence = sentence_object["S"]
    og_html = f"<p><div class='sentence'>{sentence}</div></p>"
    
    if verbose: print("S =", sentence)
    
    # result.append(f"<b>Corrections:</b><br>")
    
    current_annotator_id = 0
    current_output_html_str = ""
    current_output_tokens = sentence.split()            # tokens for annotated (+ X) (- X) HTML
    current_corrected_output_tokens = sentence.split()  # tokens for corrected text HTML
    
    for edit_id, edit_str in enumerate(sentence_object["A"]):
        if verbose: print("Edit =", edit_str)
        edit_obj = parse_edit_string(edit_str=edit_str, sentence=sentence)
        if verbose: print("Edit object =", edit_obj)
        
        if edit_obj.get("annotator_id") != current_annotator_id:
            # add current html string to the output
            if sen_tag:
                current_corrected_output_html_str = f"<p><div class='sentence'>{' '.join(current_corrected_output_tokens)}</div></p>"
                current_output_html_str = f"<p><div class='sentence'>{' '.join(current_output_tokens)}</div></p>"
            else:
                current_corrected_output_html_str = f"{' '.join(current_corrected_output_tokens)}"
                current_output_html_str = f"{' '.join(current_output_tokens)}"

            # store current sentence html
            anno_htmls.append(current_output_html_str)
            corr_htmls.append(current_corrected_output_html_str)
                        
            # reset current html string
            current_output_html_str = ""
            current_output_html_str = ""
            current_output_tokens = sentence.split()
            current_corrected_output_tokens = sentence.split()
            
            current_annotator_id = edit_obj.get("annotator_id")
            if verbose: print("New annotator detected:", current_annotator_id)

        HTML_tags = HTML_TAGS_WB
        
        if edit_obj.get("type").startswith("M:"): # Missing
            if edit_obj.get("o_start") < len(current_output_tokens):
                current_output_tokens[edit_obj.get("o_start")] =(f"{HTML_tags.get('insert_start')} {edit_obj.get('c_str')}{HTML_tags.get('insert_end')} " + 
                                                                  current_output_tokens[edit_obj.get("o_start")]
                                                                 )

                # modify corrected text
                current_corrected_output_tokens[edit_obj.get("o_start")] =(f"<b>{edit_obj.get('c_str')}</b> " + 
                                                                           current_corrected_output_tokens[edit_obj.get("o_start")]
                                                                          )
            else: 
                # add something at the end of the sentence
                current_output_tokens.append(f"{HTML_tags.get('insert_start')} {edit_obj.get('c_str')}{HTML_tags.get('insert_end')} ")

                # modify corrected text
                current_corrected_output_tokens.append(f"<b>{edit_obj.get('c_str')}</b>")
            
            pass
        elif edit_obj.get("type").startswith("U:"): # Unnecessary
            current_output_tokens[edit_obj.get("o_start")] = (f"{HTML_tags.get('remove_start')} " + 
                                                              current_output_tokens[edit_obj.get("o_start")]
                                                             )
            current_output_tokens[edit_obj.get("o_end")-1] += HTML_tags.get('remove_end')

            # modify corrected text
            for token_id in range(edit_obj.get("o_start"), edit_obj.get("o_end")):
                # clear all unnecessary tokens
                current_corrected_output_tokens[token_id] = ""
                
        elif edit_obj.get("type").startswith("R:"): # Replacement
            current_output_tokens[edit_obj.get("o_start")] = (f"{HTML_tags.get('remove_start')} " + 
                                                              current_output_tokens[edit_obj.get("o_start")]
                                                             )
            current_output_tokens[edit_obj.get("o_end")-1] += (HTML_tags.get('remove_end') + 
                                                              f" {HTML_tags.get('insert_start')} {edit_obj.get('c_str')}{HTML_tags.get('insert_end')}"
                                                              )
                                                             
            # modify corrected text
            for token_id in range(edit_obj.get("o_start"), edit_obj.get("o_end")):
                # clear all unnecessary tokens
                current_corrected_output_tokens[token_id] = ""
    
            # add new corrected text
            current_corrected_output_tokens[edit_obj.get("o_start")] = f"<b>{edit_obj.get('c_str')}</b>"
    
    # add last html result to the output
    if sen_tag:
        current_corrected_output_html_str = f"<p><div class='sentence'>{' '.join(current_corrected_output_tokens)}</div></p>"
        current_output_html_str = f"<p><div class='sentence'>{' '.join(current_output_tokens)}</div></p>"
    else: 
        current_corrected_output_html_str = f"{' '.join(current_corrected_output_tokens)}"
        current_output_html_str = f"{' '.join(current_output_tokens)}"


    # store current sentence html
    anno_htmls.append(current_output_html_str)
    corr_htmls.append(current_corrected_output_html_str)

    return og_html, anno_htmls, corr_htmls

# heavily modified from code by github.com/minhngca
# returns the html for the original sentence and a selected annotation for each model
# enables showing and hiding the annotations/corrections
def sentence_to_html(sentence_object, tagless_mode=False):
    if not tagless_mode:
        og_html, anno_htmls, corr_htmls = annotations_to_html(sentence_object)
    else:
        og_html, anno_htmls, corr_htmls = annotations_to_html(sentence_object, sen_tag=False)

    return og_html, anno_htmls[0], corr_htmls[0]
