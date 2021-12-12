import os
from sentence_parser import *
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller,SentenceSplitter


class TripleExtractor:
    def __init__(self):
        self.parser = LtpParser()

    def SRL(self, words, postags, roles_dict, role_index):
        v = words[role_index]
        index_key=roles_dict.keys()
        if role_index in index_key:
            role_info = roles_dict[role_index]
            if 'A0' in role_info.keys() and 'A1' in role_info.keys():
                s = ''.join([words[word_index] for word_index in range(role_info['A0'][1], role_info['A0'][2] + 1) if
                             postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
                o = ''.join([words[word_index] for word_index in range(role_info['A1'][1], role_info['A1'][2] + 1) if
                             postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
                if s and o:
                    return '1', [s, v, o]
            elif 'A1' in role_info.keys():
                o = ''.join([words[word_index] for word_index in range(role_info['A1'][1], role_info['A1'][2] + 1) if
                             postags[word_index][0] not in ['w', 'u', 'x'] and words[word_index]])
                if  o:
                    return '2', [v, o]

        return '4', []


    def entity(self, words, postags, child_dict_list, arcs, roles_dict):
        svos = []
        for index in range(len(postags)):
            tmp = 1

            flag, triple = self.SRL(words, postags, roles_dict, index)
            if flag == '1':
                svos.append(triple)
                tmp = 0
            if tmp == 1:

                # if postags[index] == 'v':
                if postags[index]:

                    child_dict = child_dict_list[index]
                    # 主谓宾
                    if 'SBV' in child_dict and 'VOB' in child_dict:
                        r = words[index]
                        e1 = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
                        e2 = self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
                        svos.append([e1, r, e2])


                    relation = arcs[index][0]
                    head = arcs[index][2]
                    if relation == 'ATT':
                        if 'VOB' in child_dict:
                            e1 = self.complete_e(words, postags, child_dict_list, head - 1)
                            r = words[index]
                            e2 = self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
                            temp_string = r + e2
                            if temp_string == e1[:len(temp_string)]:
                                e1 = e1[len(temp_string):]
                            if temp_string not in e1:
                                svos.append([e1, r, e2])

                    if 'SBV' in child_dict and 'CMP' in child_dict:
                        e1 = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0])
                        cmp_index = child_dict['CMP'][0]
                        r = words[index] + words[cmp_index]
                        if 'POB' in child_dict_list[cmp_index]:
                            e2 = self.complete_e(words, postags, child_dict_list, child_dict_list[cmp_index]['POB'][0])
                            svos.append([e1, r, e2])

        return svos


    def complete_e(self, words, postags, child_dict_list, word_index):
        child_dict = child_dict_list[word_index]
        prefix = ''
        if 'ATT' in child_dict:
            for i in range(len(child_dict['ATT'])):
                prefix += self.complete_e(words, postags, child_dict_list, child_dict['ATT'][i])
        postfix = ''
        if postags[word_index] == 'v':
            if 'VOB' in child_dict:
                postfix += self.complete_e(words, postags, child_dict_list, child_dict['VOB'][0])
            if 'SBV' in child_dict:
                prefix = self.complete_e(words, postags, child_dict_list, child_dict['SBV'][0]) + prefix

        return prefix + words[word_index] + postfix

    def triples_main(self, sentence):
        words, postags, child_dict_list, roles_dict, arcs = self.parser.parser_main(sentence)
        svo = self.entity(words, postags, child_dict_list, arcs, roles_dict)

        print(svo)
        # sentences = self.split_sents(content)
        # svos = []
        # for sentence in sentences:
        #     words, postags, child_dict_list, roles_dict, arcs = self.parser.parser_main(sentence)
        #     svo = self.ruler2(words, postags, child_dict_list, arcs, roles_dict)
        #     svos += svo
        #
        # return svos



def test():
    
    f = open("symptom_description_clean.txt", "r")
    symptom_desciption = f.read()
    paragraph = symptom_desciption
    # --------------------- 断句 ------------------------
    sentence = SentenceSplitter.split(paragraph)[0]
    extractor = TripleExtractor()
    svos = extractor.triples_main(sentence)

    #content5='典型的产后抑郁症的症状类似于重型抑郁症，主要表现焦虑和抑郁心境，疲劳、睡眠障碍、食欲异常、记忆力下降、注意力不集中，感到内疚、羞愧、愤怒，没有能力或无望感，存在自杀想法或自杀行为，有时出现强迫观念或行为，怕出门，对自己、小孩及伴侣过分关心，怕发生不幸事件等。'


test()
