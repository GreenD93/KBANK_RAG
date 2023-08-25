import openai
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

PROMPT_DICT = {
    "prompt_input" : (
        "서비스 센터 직원처럼 응답해주세요.\n\n"
        "응답할 때, 모든 문서를 참고하세요.\n"
        "응답할 때, 상품정보를 참고하세요.\n"
        "응답할 때, 금리와 관련이 있는 질문은 반드시 금리도 함께 알려주세요.\n"
        "응답할 때, Instruction에 대한 내용을 짧게 정리해주세요.\n\n"
        "### 문서 :\n{docs}\n\n"
        "### 상품정보 :\n{prd_info}\n\n"
        "### Instruction(명령어):\n{instruction}\n\n### Response(응답):"
    )
}

class SearchHandler:
    
    def __init__(self, items, prd_infos):
        
        self.index = None
        self.model = None
        
        self.items = items
        self.prd_infos = prd_infos
        
        self.pd_dic = {
            "플러스박스" : ["플러스박스","플박"],
            "챌린지박스" : ["챌린지박스","챌박"],
            "MY입출금통장": ["MY입출금통장","입출금통장"],
            "코드K정기예금": ["코드K정기예금","정기예금","예금"],
            "주거래자유적금": ["주거래우대자유적금","주거래적금","주거래"],
            "코드K자유적금": ["코드K자유적금","자유적금"],
            "아파트담보대출": ["아파트담보대출","아담대"],
            "전세대출": ["전세대출","전세"],
            "예금적금담보대출": ["예금적금담보대출"],
            "신용대출": ["신용대출"],
            "마이너스통장": ["마이너스통장","마이너스대출","마통"],
            "비상금대출": ["비상금대출"],
            "사잇돌대출": ["사잇돌대출"],
            "대출갈아타기": ["대출갈아타기","대환"],
            "사장님신용대출": ["사장님신용대출","사장님대출"],
            "사장님보증서대출": ["사장님보증서대출"],
            "MY체크카드": ["MY체크카드","알뜰"],
            "플러스체크카드": ["플러스체크카드"],
            "KT멤버십더블혜택체크카드": ["KT멤버십더블혜택체크카드","KT체크카드"],
            "HITEEN카드": ["HITEEN카드", "하이틴"]
        }
        pass
    
    def set_openai_key(self, key):
        openai.api_key = key
        pass
        
    def load_index(self, index_path):
        index = faiss.read_index(index_path)
        self.index = index
        pass
    
    def load_model(self, model_path):
        model = SentenceTransformer(model_path)
        self.model = model
        pass
    
    def get_embedding(self, query):
        return self.model.encode(query)
        
    def search_prd(self, query):
        
        query = query.replace(" ","").upper()
        
        for prd, values in self.pd_dic.items():
            for value in values:
                if value in query:
                    return prd
                
        return None
    
    def search_docs(self, embed, thresh=50):
        
        # thresh hold기반
        limits, distances, indices = self.index.range_search(embed, thresh)
        
        # 가장 유사한거 1개
        dists, idxs = self.index.search(embed, 1)
        
        indices = indices.tolist() + idxs[0].tolist()
        indices = list(set(indices))
        
        docs = []

        for indice in indices:
            doc = self.items[indice]['answer']
            docs.append(doc)
        
        return docs
         
    def make_request(self, query, thresh=50):
        
        embed = self.get_embedding(query)
        embed = np.array(embed).reshape(1,-1)
        
        docs = self.search_docs(embed, thresh)
        prd = self.search_prd(query)
        
        if len(docs) == 0 and prd == None:
            
            request = {
                "code" : 0,
                "prompt" : None
            }

        else:
            
            if prd != None:
                prd_info = prd + ':\n' + self.prd_infos[prd]
            else:
                prd_info = None

            if len(docs) > 0:

                doc_str = ""

                for i, doc in enumerate(docs):

                    no = i + 1
                    doc_str += f"\n{no}.\n{doc}\n"
            else:
                doc_str = None

            prompt = PROMPT_DICT["prompt_input"].format(docs=doc_str, prd_info=prd_info, instruction=query)
            
            request = {
                "code" : 1,
                "prompt" : prompt
            }
            
        return request
    
    def get_response(self, query):
        
        request = self.make_request(query)
        
        code, prompt = request['code'], request['prompt']
        
        print(prompt)
        
        if code == 1:
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                      {
                          "role": "user", 
                          "content": prompt
                      }
                  ]
            )

            response = response["choices"][0]["message"]["content"]
            
        elif code == 0:
            
            response = "잘 모르겠습니다. 다른 내용을 물어봐주시면 친절하게 설명 드리겠습니다."
        
        return response
