import os
from pyltp import Segmentor, Postagger, Parser, NamedEntityRecognizer, SementicRoleLabeller

class LtpParser:
    def __init__(self):
        LTP_DIR = "/Users/wjcz/anaconda2/envs/CounselingKG /model"
        self.segmentor = Segmentor(model_path=os.path.join(LTP_DIR, "cws.model"))
        # self.segmentor.load(os.path.join(LTP_DIR, "cws.model"))

        self.postagger = Postagger(model_path=os.path.join(LTP_DIR, "pos.model"))
        # self.postagger.load(os.path.join(LTP_DIR, "pos.model"))

        self.parser = Parser(os.path.join(LTP_DIR, "parser.model"))
        # self.parser.load(os.path.join(LTP_DIR, "parser.model"))

        self.recognizer = NamedEntityRecognizer(os.path.join(LTP_DIR, "ner.model"))
        # self.recognizer.load(os.path.join(LTP_DIR, "ner.model"))

        self.labeller = SementicRoleLabeller(os.path.join(LTP_DIR, 'pisrl.model'))
        # self.labeller.load(os.path.join(LTP_DIR, 'pisrl_win.model'))


    def format_labelrole(self, words, postags):
        arcs = self.parser.parse(words, postags)
        roles = self.labeller.label(words, postags, arcs)
        roles_dict = {}
        for index,role in roles:
            roles_dict[index] = {name:[name,arg[0], arg[1]] for name,arg in role}
        # for role in roles:
        #     roles_dict[role.index] = {arg.name:[arg.name,arg.range.start, arg.range.end] for arg in role.arguments}
        return roles_dict


    def build_parse_child_dict(self, words, postags, arcs):
        child_dict_list = []
        format_parse_list = []
        for index in range(len(words)):
            child_dict = dict()
            for idx,(head,relation) in enumerate(arcs):
                if head == index + 1: #arcs的索引从1开始，head 表示依存弧的父节点的索引。root节点的索引是0，从第一个词开始索引依次为1，2，3，。。。relation表示依存弧的关系。
                    if relation in child_dict:
                        child_dict[relation].append(idx)
                    else:
                        child_dict[relation] = []
                        child_dict[relation].append(idx)
            # for arc_index in range(len(arcs)):
            #     if arcs[arc_index].head == index+1:
            #         if arcs[arc_index].relation in child_dict:
            #             child_dict[arcs[arc_index].relation].append(arc_index)#添加
            #         else:
            #             child_dict[arcs[arc_index].relation] = []#新建
            #             child_dict[arcs[arc_index].relation].append(arc_index)
            child_dict_list.append(child_dict)

        rely_id = [head for head,relation in arcs]  # 提取依存父节点id
        relation = [relation for head,relation in arcs]  # 提取依存关系
        heads = ['Root' if id == 0 else words[id - 1] for id in rely_id]  # 匹配依存父节点词语
        for i in range(len(words)):
            a = [relation[i], words[i], i, postags[i], heads[i], rely_id[i]-1, postags[rely_id[i]-1]]
            format_parse_list.append(a)

        return child_dict_list, format_parse_list


    def parser_main(self, sentence):
        words = list(self.segmentor.segment(sentence))
        postags = list(self.postagger.postag(words))
        arcs = self.parser.parse(words, postags)
        child_dict_list, format_parse_list = self.build_parse_child_dict(words, postags, arcs)
        roles_dict = self.format_labelrole(words, postags)
        return words, postags, child_dict_list, roles_dict, format_parse_list


if __name__ == '__main__':
    parse = LtpParser()

    sentence = '典型的产后抑郁症的症状类似于重型抑郁症，主要表现焦虑和抑郁心境，疲劳、睡眠障碍、食欲异常、记忆力下降、注意力不集中，感到内疚、羞愧、愤怒，没有能力或无望感，存在自杀想法或自杀行为，有时出现强迫观念或行为，怕出门，对自己、小孩及伴侣过分关心，怕发生不幸事件等。'

    words, postags, child_dict_list, roles_dict, format_parse_list = parse.parser_main(sentence)
    print(words, len(words))
    print(postags, len(postags))
    print(child_dict_list, len(child_dict_list))
    print(roles_dict)
    print(format_parse_list, len(format_parse_list))
