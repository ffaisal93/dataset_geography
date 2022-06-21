from genre.fairseq_model import mGENRE
import pickle
from genre.trie import Trie, MarisaTrie
import sys
import pickle
import os
import subprocess
import multiprocessing
import itertools
from log import logger




def ParallelExtractDir(sentence):
    try:
        news=[sentence]
        one = model.sample(
                news,
                prefix_allowed_tokens_fn=lambda batch_id, sent: [
                    e for e in trie.get(sent.tolist()) if e < len(model.task.target_dictionary)
                ],
                text_to_id=lambda x: max(lang_title2wikidataID[tuple(reversed(x.split(" >> ")))], key=lambda y: int(y[1:])),
                marginalize=True,
            )
        return one[0]
    except IndexError:
        logger.info(news)
        return ''




def check_out(name):
    out_root  = '../outputs'
    result = False
    for x in os.listdir(out_root):
        discarded = ['.DS_Store']
        if name==str(x[:-7]):
            result= True
            break
        else:
            result= False
    return result


def do_operation(sentences):
    p = multiprocessing.Pool(12)
    alls = p.map(ParallelExtractDir, sentences)

    with open('../outputs/{}.pickle'.format(name),'wb') as f:
        pickle.dump(alls, f)


if __name__ == "__main__":
    datafile = str(sys.argv[1])
    name=str(sys.argv[2])
    outpath=str(sys.argv[3])
    print(name)
    if check_out(name)==True:
        logger.info('file exist')
    else:
        with open(datafile,'rb') as f:
            sentences =  pickle.load(f)
        logger.info('{} file loaded'.format(name))
        
        ##load models
        model_mlpath = "../models/fairseq_multilingual_entity_disambiguation"
        trie_path = "../models/titles_lang_all105_marisa_trie_with_redirect.pkl"
        lang_2_title_path = "../models/lang_title2wikidataID-normalized_with_redirect.pkl"

        model = mGENRE.from_pretrained(model_mlpath).eval()
        logger.info('model loaded')

        with open(trie_path, "rb") as f:
            trie = pickle.load(f)

        logger.info('trie loaded')

        with open(lang_2_title_path, "rb") as f:
            lang_title2wikidataID = pickle.load(f)
        logger.info('wikimap loaded')
        # do_operation(sentences)

        temp_path = '{}/{}-temp.pickle'.format(outpath, name)
        out_path = '{}/{}.pickle'.format(outpath, name)
        left_sent = []
        if os.path.exists(temp_path)==True:
            with open(temp_path,'rb') as f:
                done_sent =  pickle.load(f)
            left_sent = sentences[len(done_sent):]
            sent_save=done_sent
        else:
            left_sent = sentences
            sent_save = []
        logger.info('left sent:{}, done_sent:{}'.format(len(left_sent),len(sent_save)))


        for i in range(0,len(left_sent),200):
            try:
                news=left_sent[i:i+200]
                one = model.sample(
                        news,
                        prefix_allowed_tokens_fn=lambda batch_id, sent: [
                            e for e in trie.get(sent.tolist()) if e < len(model.task.target_dictionary)
                        ],
                        text_to_id=lambda x: max(lang_title2wikidataID[tuple(reversed(x.split(" >> ")))], key=lambda y: int(y[1:])),
                        marginalize=True,
                    )
                sent_save.extend(one)
            except Exception as err:
                for k,sent in enumerate(news):
                    try:
                        news1=[sent]
                        one = model.sample(
                                news1,
                                prefix_allowed_tokens_fn=lambda batch_id, sent: [
                                    e for e in trie.get(sent.tolist()) if e < len(model.task.target_dictionary)
                                ],
                                text_to_id=lambda x: max(lang_title2wikidataID[tuple(reversed(x.split(" >> ")))], key=lambda y: int(y[1:])),
                                marginalize=True,
                            )
                        sent_save.append(one[0])
                    except Exception as err1:
                        logger.info(news1)
                        sent_save.append('')

                logger.info('error:-------------------------{}-{}'.format(i,i+200))
            if i%200==0:
                logger.info('total done: {}, left:{}'.format(len(sent_save), len(left_sent)-i))
                with open(temp_path,'wb') as f:
                    pickle.dump(sent_save, f)        

        with open(out_path,'wb') as f:
            pickle.dump(sent_save, f)
        
        if os.path.isfile(temp_path):
            os.remove(temp_path)



