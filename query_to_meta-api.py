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
    tag_set = ['Ambient','R & B','SF','Vlog','World','가족','감동','고양','광고','광고하는','교육','그루비',
                '극도의','기술','냉기','뉴스','뉴에이지','다큐멘터리','댄스','동양적인','드라마','드럼 &베이스','듣기 쉬운',
                '라이프 스타일','라틴','락','레저','로맨틱','메탈','무서운','범죄','블로그','블루스','비디오 게임','섹시한',
                '소름','소울','쉬운 듣기','스포츠','슬로 모션','슬로우모션','시사','신나는','신비','어린이','여행','역사',
                '영화','오케스트라','웃기는','일렉트로닉','재즈','저속 촬영','전자','카페','컨트리',
                '코메디','클래식','타임랩스','팝','패션','펑키','펑키 재즈','평화로운','포크','희망','힙합']
    search_song_indices = [model.wv.vocab[str(x)].index for x in audio_meta.keys() if str(x) in model.wv.vocab]
    tag_indices = [model.wv.vocab[str(x)].index for x in tag_set if str(x) in model.wv.vocab]
    print("Finish Loading Audio & Meta Data")

    app.run(host=host, port=port)
