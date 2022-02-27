import itertools



noun_tags_lst = ['NN', 'NNS', 'WP', 'PRP', 'NNP', 'NNPS']




dep_type_optional = ['amod', 'compound', 'det', 'advmod', 'dobj', 'mark', 'npadvmod', 'nmod',
                     'appos', 'nummod', 'nsubj', 'conj']  # , 'conj'

prep_to_seq = ['prep', 'pobj', 'amod', 'pcomp', 'pobj']  # prep and agent
acl_to_seq = ['acomp', 'prep', 'dobj']  # acl and relcl + [[['xcomp'], ['aux']], 'dobj']
poss_to_seq = ['case']
others_to_seq = ['cc', 'appos', 'quantmod', 'nsubjpass', 'aux', 'poss']
combined_with = ['acl', 'relcl', 'prep', 'agent', 'poss']  # +, 'cc'
couple_to_seq = {'cc': ['conj', 'nmod'], 'quantmod': ['amod'], 'nsubjpass': ['amod'], 'aux': ['auxpass']}







def get_all_valid_sub_special(token, special_to_seq, next_catch_word_index):
    sub_np_lst = []
    for child in token.children:
        if child.i >= next_catch_word_index:
            continue
        sub_np = []
        if child.dep_ in special_to_seq:
            if child.dep_ == 'prep' or child.dep_ == 'agent':
                all_sub_of_sub = get_all_valid_sub_special(child, prep_to_seq, next_catch_word_index)
                all_sub_of_sub = [token] + all_sub_of_sub
                sub_np.append(all_sub_of_sub)
                if sub_np:
                    sub_np_lst.extend(sub_np)
            else:
                all_sub_of_sub = get_all_valid_sub_np(child, next_catch_word_index)
                all_sub_of_sub = [token] + all_sub_of_sub
                sub_np.append(all_sub_of_sub)
                if sub_np:
                    sub_np_lst.extend(sub_np)
    if not sub_np_lst:
        return []
    # sub_np_lst = [token] + sub_np_lst
    return sub_np_lst


def from_children_to_list(children):
    lst_children = []
    for token in children:
        lst_children.append(token)
    return lst_children


def get_det_token_from_children(lst_children):
    for child in lst_children:
        if child.dep_ == 'det':
            lst_children.remove(child)
            return child
    return None


def set_couple_deps(couple_lst, next_catch_word_index, sub_np_lst):
    for couple in couple_lst:
        lst_children_first = from_children_to_list(couple[0].children)
        det_node_first = get_det_token_from_children(lst_children_first)
        lst_children_second = from_children_to_list(couple[1].children)
        det_node_second = get_det_token_from_children(lst_children_second)
        if det_node_first:
            sub_np_lst_couple = [det_node_first, couple[0]]
        else:
            sub_np_lst_couple = [couple[0]]
        if det_node_second:
            sub_np_lst_couple.append(det_node_second, couple[1])
        else:
            sub_np_lst_couple.append(couple[1])
        all_sub_of_sub = []
        get_children_expansion(all_sub_of_sub, lst_children_first, next_catch_word_index)
        get_children_expansion(all_sub_of_sub, lst_children_second, next_catch_word_index)
        if all_sub_of_sub:
            sub_np_lst_couple.append(all_sub_of_sub)
        sub_np_lst.append(sub_np_lst_couple)


def initialize_couple_lst(others, couple_lst, lst_children):
    for other in others:
        dep_type = couple_to_seq[other.dep_]
        for token in lst_children:
            if token.dep_ in dep_type:
                couple_lst.append([other, token])


def get_token_by_dep(lst_children, dep_type):
    for child in lst_children:
        if child.dep_ == dep_type:
            return child
    return None

def remove_conj_if_cc_exist(lst_children):
    cc_is_exist = False
    for child in lst_children:
        if child.dep_ == 'cc':
            cc_is_exist = True
    if cc_is_exist:
        child = get_token_by_dep(lst_children, 'conj')
        if child is None:
            child = get_token_by_dep(lst_children, 'nmod')
        if child:
            return [child]
        return []
    return []




def get_children_expansion(sub_np_lst, lst_children, next_catch_word_index):
    others = []
    lst_to_skip = remove_conj_if_cc_exist(lst_children)
    for child in lst_children:
        if child in lst_to_skip:
            continue
        if child.i >= next_catch_word_index:
            continue
        sub_np = []
        if child.dep_ in dep_type_optional:
            all_sub_of_sub = get_all_valid_sub_np(child, next_catch_word_index)
            sub_np.append(all_sub_of_sub)
            if sub_np:
                sub_np_lst.extend(sub_np)
        elif child.dep_ in combined_with:
            if child.dep_ == 'prep' or child.dep_ == 'agent':
                all_sub_of_sub = get_all_valid_sub_special(child, prep_to_seq, next_catch_word_index)
            elif child.dep_ == 'acl' or child.dep_ == 'relcl':
                all_sub_of_sub = get_all_valid_sub_special(child, acl_to_seq, next_catch_word_index)
            elif child.dep_ == 'poss':
                all_sub_of_sub = get_all_valid_sub_special(child, poss_to_seq, next_catch_word_index)
                if all_sub_of_sub == []:
                    all_sub_of_sub = get_all_valid_sub_np(child, next_catch_word_index)
            if all_sub_of_sub:
                sub_np.append(all_sub_of_sub)
            if sub_np:
                sub_np_lst.extend(sub_np)
        elif child.dep_ in others_to_seq:
            others.append(child)
        else:
            if child.dep_ != 'punct':
                print(child.dep_)
    couple_lst = []
    if others:
        initialize_couple_lst(others, couple_lst, lst_children)
    set_couple_deps(couple_lst, next_catch_word_index, sub_np_lst)
    # return others

def powerset(iterable):
    # s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(iterable, r) for r in range(len(iterable)+1))

def get_all_valid_sub_np(head, next_catch_word_index):
    lst_children = from_children_to_list(head.children)
    det_node = get_det_token_from_children(lst_children)
    if det_node:
        sub_np_lst = [det_node, head]
    else:
        sub_np_lst = [head]
    get_children_expansion(sub_np_lst, lst_children, next_catch_word_index)
    return sub_np_lst


def from_lst_to_sequence(sub_np_final_lst, sub_np_lst, current_lst):
    if isinstance(sub_np_lst[0], list):
        return from_lst_to_sequence(sub_np_final_lst, sub_np_lst[0], current_lst)
    else:
        collect_to_lst = []
        slice_index = 0
        for item in sub_np_lst:
            if isinstance(item, list):
                break
            collect_to_lst.append(item)
            slice_index += 1
        current_lst.extend(collect_to_lst)
    if len(sub_np_lst) == 1:
        return [current_lst]
    sub_np_of_child_lst = []
    for child in sub_np_lst[slice_index:]:
        new_lst_for_child = current_lst.copy()
        sub_np_of_child = from_lst_to_sequence(sub_np_final_lst, child, new_lst_for_child)
        sub_np_of_child_lst.append(sub_np_of_child)
    result_list = list(powerset(sub_np_of_child_lst))
    sub_np_of_child_lst_final = []
    for item in result_list:
        for element in itertools.product(*item):
            if item == ():
                continue
            lst_temp = []
            for token in element:
                lst_temp.extend(token)
            sub_np_of_child_lst_final.append(list(set(lst_temp)))
    sub_np_of_child_lst_final.append(current_lst)
    return sub_np_of_child_lst_final



def is_np_child_head(head_word, word):
    if word.head == head_word:
        return True
    if word == word.head:
        return False
    return is_np_child_head(head_word, word.head)


def get_np_boundary(head_word_index, sentence_dep_graph):
    head_word = sentence_dep_graph[head_word_index]
    if head_word.tag_ not in noun_tags_lst:
        return None, None
    boundary_np_to_the_left = head_word_index
    # np's boundary to the left
    for i in range(1, head_word_index + 1):
        current_index = head_word_index - i
        word = sentence_dep_graph[current_index]
        if is_np_child_head(head_word, word):
            boundary_np_to_the_left = current_index
            continue
        break
    # np's boundary to the right
    boundary_np_to_the_right = head_word_index
    for i in range(head_word_index + 1, len(sentence_dep_graph)):
        word = sentence_dep_graph[i]
        if is_np_child_head(head_word, word):
            boundary_np_to_the_right = i
            continue
        break
    return sentence_dep_graph[
           boundary_np_to_the_left:boundary_np_to_the_right + 1], head_word_index - boundary_np_to_the_left


def get_tokens_as_span(tokens):
    span = ""
    idx = 0
    for token in tokens:
        if idx != 0 and token.text != ',':
            span += ' '
        span += token.text
        idx += 1
    return span

def write_to_file_dict_counter(sub_np_final_lst_collection, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for sub_np_final_lst in sub_np_final_lst_collection:
            for tokens in sub_np_final_lst:
                span = get_tokens_as_span(tokens)
                f.write(span)
                f.write('\n')
            f.write('\n')