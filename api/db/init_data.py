#
#  Copyright 2024 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import json
import os
import time
import uuid
from copy import deepcopy

from api.db import LLMType, UserTenantRole
from api.db.db_models import init_database_tables as init_web_db, LLMFactories, LLM, TenantLLM
from api.db.services import UserService
from api.db.services.canvas_service import CanvasTemplateService
from api.db.services.document_service import DocumentService
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.db.services.llm_service import LLMFactoriesService, LLMService, TenantLLMService, LLMBundle
from api.db.services.user_service import TenantService, UserTenantService
from api.settings import CHAT_MDL, EMBEDDING_MDL, ASR_MDL, IMAGE2TEXT_MDL, PARSERS, LLM_FACTORY, API_KEY, LLM_BASE_URL
from api.utils.file_utils import get_project_base_directory


def init_superuser():
    user_info = {
        "id": uuid.uuid1().hex,
        "password": "admin",
        "nickname": "admin",
        "is_superuser": True,
        "email": "admin@ragflow.io",
        "creator": "system",
        "status": "1",
    }
    tenant = {
        "id": user_info["id"],
        "name": user_info["nickname"] + "‘s Kingdom",
        "llm_id": CHAT_MDL,
        "embd_id": EMBEDDING_MDL,
        "asr_id": ASR_MDL,
        "parser_ids": PARSERS,
        "img2txt_id": IMAGE2TEXT_MDL
    }
    usr_tenant = {
        "tenant_id": user_info["id"],
        "user_id": user_info["id"],
        "invited_by": user_info["id"],
        "role": UserTenantRole.OWNER
    }
    tenant_llm = []
    for llm in LLMService.query(fid=LLM_FACTORY):
        tenant_llm.append(
            {"tenant_id": user_info["id"], "llm_factory": LLM_FACTORY, "llm_name": llm.llm_name, "model_type": llm.model_type,
             "api_key": API_KEY, "api_base": LLM_BASE_URL})

    if not UserService.save(**user_info):
        print("\033[93m【ERROR】\033[0mcan't init admin.")
        return
    TenantService.insert(**tenant)
    UserTenantService.insert(**usr_tenant)
    TenantLLMService.insert_many(tenant_llm)
    print(
        "【INFO】Super user initialized. \033[93memail: admin@ragflow.io, password: admin\033[0m. Changing the password after logining is strongly recomanded.")

    chat_mdl = LLMBundle(tenant["id"], LLMType.CHAT, tenant["llm_id"])
    print("【Lynn1-Debug】chat init ok!",tenant["id"], LLMType.CHAT, tenant["llm_id"])
    msg = chat_mdl.chat(system="", history=[
                        {"role": "user", "content": "Hello!"}], gen_conf={})
    print("【Lynn1-Debug】chat test:",msg)
    if msg.find("ERROR: ") == 0:
        print(
            "\33[91m【ERROR】\33[0m: ",
            "'{}' dosen't work. {}".format(
                tenant["llm_id"],
                msg))
    embd_mdl = LLMBundle(tenant["id"], LLMType.EMBEDDING, tenant["embd_id"])
    print("【Lynn1-Debug】embd init ok!",tenant["id"], LLMType.EMBEDDING, tenant["embd_id"])
    v, c = embd_mdl.encode(["Hello!"])
    print("【Lynn1-Debug】embd test:",v)
    if c == 0:
        print(
            "\33[91m【ERROR】\33[0m:",
            " '{}' dosen't work!".format(
                tenant["embd_id"]))


factory_infos = [
    {
    "name": "Ollama",
    "logo": "",
    "tags": "LLM,TEXT EMBEDDING,SPEECH2TEXT,MODERATION",
    "status": "1",
},{
    "name": "BAAI",
    "logo": "",
    "tags": "TEXT EMBEDDING, TEXT RE-RANK",
    "status": "1",
}
]


def init_llm_factory():
    llm_infos = [
        # ------------------------ Ollama -----------------------
        {
            "fid": factory_infos[0]["name"],
            "llm_name": "bge-m3",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 8192,
            "model_type": LLMType.EMBEDDING.value
        }, 
        {
            "fid": factory_infos[0]["name"],
            "llm_name": "qwen2-embeddings",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 32768,
            "model_type": LLMType.EMBEDDING.value
        },
        {
            "fid": factory_infos[0]["name"],
            "llm_name": "qwen2",
            "tags": "LLM,CHAT,32K",
            "max_tokens": 32768,
            "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[0]["name"],
            "llm_name": "qwen2:72b",
            "tags": "LLM,CHAT,32K",
            "max_tokens": 32768,
             "model_type": LLMType.CHAT.value
        },
        {
            "fid": factory_infos[0]["name"],
            "llm_name": "llava",
            "tags": "LLM,CHAT,32K",
            "max_tokens": 32768,
            "model_type": LLMType.CHAT.value + "," + LLMType.IMAGE2TEXT.value
        },
        # ------------------------ BAAI -----------------------
        {
            "fid": factory_infos[1]["name"],
            "llm_name": "BAAI/bge-large-zh-v1.5",
            "tags": "TEXT EMBEDDING,",
            "max_tokens": 1024,
            "model_type": LLMType.EMBEDDING.value
        },
        {
            "fid": factory_infos[1]["name"],
            "llm_name": "BAAI/bge-reranker-v2-m3",
            "tags": "RE-RANK,2k",
            "max_tokens": 2048,
            "model_type": LLMType.RERANK.value
        },
    ]
    for info in factory_infos:
        try:
            LLMFactoriesService.save(**info)
        except Exception as e:
            pass
    for info in llm_infos:
        try:
            LLMService.save(**info)
        except Exception as e:
            pass

    for kb_id in KnowledgebaseService.get_all_ids():
        KnowledgebaseService.update_by_id(kb_id, {"doc_num": DocumentService.get_kb_doc_count(kb_id)})
    """
    drop table llm;
    drop table llm_factories;
    update tenant set parser_ids='naive:General,qa:Q&A,resume:Resume,manual:Manual,table:Table,paper:Paper,book:Book,laws:Laws,presentation:Presentation,picture:Picture,one:One';
    alter table knowledgebase modify avatar longtext;
    alter table user modify avatar longtext;
    alter table dialog modify icon longtext;
    """


def add_graph_templates():
    dir = os.path.join(get_project_base_directory(), "graph", "templates")
    for fnm in os.listdir(dir):
        try:
            cnvs = json.load(open(os.path.join(dir, fnm), "r"))
            try:
                CanvasTemplateService.save(**cnvs)
            except:
                CanvasTemplateService.update_by_id(cnvs["id"], cnvs)
        except Exception as e:
            print("Add graph templates error: ", e)
            print("------------", flush=True)


def init_web_data():
    start_time = time.time()

    init_llm_factory()
    if not UserService.get_all().count():
        init_superuser()

    add_graph_templates()
    print("init web data success:{}".format(time.time() - start_time))


if __name__ == '__main__':
    init_web_db()
    init_web_data()
