import argparse
import os
import json
from flask import Flask, request, jsonify, make_response
from gensim.models.keyedvectors import KeyedVectors
import functions as F

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.errorhandler(404)
def pageNotFound(error):
    return "page not found"

@app.errorhandler(500)
def raiseError(error):
    return error

@app.route('/')
def query_to_meta_api():
    doc = request.args['query']
    keyword_ex = F.keyword_extractor(doc)
    pos_tokens = F.tokenizer(" ".join(keyword_ex))
    model_input = list(set(pos_tokens))
    audio_list = F.multiquery_retrieval(model.wv, model_input, search_song_indices)
    tag_list = F.multiquery_retrieval(model.wv, model_input, tag_indices)
    result_meta = [audio_meta[audio] for audio in audio_list]
    output = {
        'query': doc,
        'model_input' : model_input,
        'tag_list': tag_list,
        'file_url': [os.path.join("http://127.0.0.1:5000/static/audio_meta/audio", i) for i in audio_list],
        'result_meta' : result_meta
    }

    return jsonify(**output)

if __name__ == "__main__":
    global model
    global audio_meta
    global search_song_indices
    global tag_indices

    parser = argparse.ArgumentParser(description='Flask option arguments')
    parser.add_argument('--host', type=str, default=None, help='Default is localhost')
    parser.add_argument('--port', type=int, default=None, help='Default is :5000')
    args = parser.parse_args() 
    host = args.host
    port = args.port

    ## Model & Meta Data Load
    model = KeyedVectors.load('./static/models/model', mmap='r')
    audio_meta = json.load(open('./static/audio_meta/meta.json', 'r'))
    tag_set = ['단순','블루스','메탈','스포츠','드라마','로맨틱','포크','댄스','흥분','베이스','라운지','신비','뉴스','리듬감','비디오 게임',
                '슬로 모션','광고','생활 양식','무서움','긴장','팝','레저','SF','영화','R&B','Vlog','가족','라이프 스타일','월드뮤직',
                '일렉트로닉','패션','카페','소울','편안','코메디','웃기는','뉴에이지','록','기분좋은','평화','펑크','힙합','다큐멘터리','교육',
                '소름','감동','희망','시사','오케스트라','드럼','타임 랩스','공간','역사','컨트리','클래식','재즈','아시아','어린이']
    search_song_indices = [model.wv.vocab[str(x)].index for x in audio_meta.keys() if str(x) in model.wv.vocab]
    tag_indices = [model.wv.vocab[str(x)].index for x in tag_set if str(x) in model.wv.vocab]
    print("Finish Loading Audio & Meta Data")

    app.run(host="0.0.0.0" , port=5000)
