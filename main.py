import spacy
import csv
from spacy import displacy
import utils as ut



nlp = spacy.load("en_core_web_sm")
used_for_examples = open('./csv/examples_used_for.csv', encoding="utf8")
output_file = './examples_used_for.txt'
csv_reader_used_for_examples = csv.reader(used_for_examples)
header = next(csv_reader_used_for_examples)
examples_to_visualize = []
counter = 0
sub_np_final_lst_collection = []
for row in csv_reader_used_for_examples:
    if counter > 200:
        break
    sentence_dep_graph = nlp(row[13])
    head_word_index = int(row[5])
    next_catch_word_index = int(row[7])
    noun_phrase, head_word_in_np_index = ut.get_np_boundary(head_word_index, sentence_dep_graph)
    if noun_phrase is None:
        continue
    examples_to_visualize.append(noun_phrase)
    all_valid_sub_np = ut.get_all_valid_sub_np(noun_phrase[head_word_in_np_index], next_catch_word_index)
    sub_np_final_lst = []
    sub_np_final_lst = ut.from_lst_to_sequence(sub_np_final_lst, all_valid_sub_np, [])
    for sub_np in sub_np_final_lst:
        sub_np.sort(key=lambda x: x.i)
    sub_np_final_lst_collection.append(sub_np_final_lst)
    counter += 1
print(counter)
ut.write_to_file_dict_counter(sub_np_final_lst_collection, output_file)
# doc = nlp("This is a sentence.")
# doc2 = nlp("My name is Itay Yair.")
displacy.serve(examples_to_visualize, style="dep", port=5000)

