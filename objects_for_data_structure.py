noun_dict = {}
valid_modifier = {}


def get_expansion_modifier(dep, modifier):
    expansion_modifier = dep.expansion_modifier_dict.get(modifier.val, None)
    if expansion_modifier:
        expansion_modifier.add_occurrence()
    else:
        modifier_object = valid_modifier.get(modifier.val, None)
        if modifier_object is None:
            modifier_object = Modifier_object(modifier.val)
            valid_modifier[modifier.val] = modifier_object
        expansion_modifier = Expansion_modifier(modifier_object)
        dep.add_expansion_modifier(expansion_modifier)
    return expansion_modifier


class Noun:
    def __init__(self, word):
        self.word = word
        self.num_of_occurrences = 0
        self.dep_dict = {}

    def fill_example_in_noun_graph(self, node, modifiers):
        if modifiers is None:
            return
        for modifier in modifiers:
            dep = node.dep_dict.get(modifier.dep, None)
            if dep:
                expansion_modifier = get_expansion_modifier(dep, modifier)
            else:
                dep = Dep(modifier.dep)
                node.dep_dict[modifier.dep] = dep
                expansion_modifier = get_expansion_modifier(dep, modifier)
            expansion_modifier.modifier_object.add_to_modifier_of_modifiers_dict(node.modifier_object.modifier)
            dep.add_expansion_modifier(expansion_modifier)
            self.fill_example_in_noun_graph(expansion_modifier, modifier.modifiers)

    def add_example(self, example):
        self.num_of_occurrences += 1
        for modifier in example:
            dep = self.dep_dict.get(modifier.dep, None)
            if dep:
                expansion_modifier = get_expansion_modifier(dep, modifier.val)
            else:
                dep = Dep(modifier.dep)
                self.dep_dict[modifier.dep] = dep
                expansion_modifier = get_expansion_modifier(dep, modifier.val)
            expansion_modifier.add_occurrence()
            expansion_modifier.modifier_object.add_to_noun_dict(self.word)
            dep.add_expansion_modifier(expansion_modifier)
            self.fill_example_in_noun_graph(expansion_modifier, modifier.modifiers)


class Dep:
    def __init__(self, type):
        self.type = type
        self.num_of_occurrences = 0
        self.expansion_modifier_dict = {}
        self.expansion_modifier_count_dict = {}

    def add_expansion_modifier(self, expansion_modifier):
        if self.expansion_modifier_dict.get(expansion_modifier.modifier_object.modifier, None) is None:
            self.expansion_modifier_dict[expansion_modifier.modifier_object.modifier] = expansion_modifier
        self.expansion_modifier_count_dict[expansion_modifier.modifier_object.modifier] = self.expansion_modifier_count_dict.get(expansion_modifier.modifier_object.modifier, 0) + 1
        self.num_of_occurrences += 1


class Expansion_modifier:
    def __init__(self, modifier_object):
        self.modifier_object = modifier_object
        self.num_of_occurrences = 0
        self.dep_dict = {}

    def add_occurrence(self):
        self.num_of_occurrences += 1
        self.modifier_object.add_occurrence()


class Modifier_object:
    def __init__(self, modifier):
        self.num_of_occurrences = 0
        self.modifier = modifier
        self.noun_dict = {}
        self.modifier_of_modifiers_dict = {}

    def add_occurrence(self):
        self.num_of_occurrences += 1

    def add_to_noun_dict(self, word):
        self.noun_dict[word] = self.noun_dict.get(word, 0) + 1

    def add_to_modifier_of_modifiers_dict(self, word):
        self.modifier_of_modifiers_dict[word] = self.modifier_of_modifiers_dict.get(word, 0) + 1


class Node:
    def __init__(self, val, dep, modifiers):
        self.val = val
        self.dep = dep
        self.modifiers = modifiers
