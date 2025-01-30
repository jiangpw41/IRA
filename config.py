from collections import OrderedDict

_ROOT_PATH = "/home/jiangpeiwen2/jiangpeiwen2/NL2GQL"

SpCQL_ALL_METHODS = OrderedDict({
    "Gold" : {
        "Gold_Query": False
    },
    "R3":{
        "Perfect_GPT": False
    },
    "Copynet" : {
        "100e": False
    },
    "FT":{
        "ChatGLM3-6B": True,
        "Qwen1.5-7B-Chat": True,
        "Chinese-Mistral-7B-Instruct-v0.1": True,
        "Mistral-7B-Instruct-v0.2": True,
        "Meta-Llama-3-8B-Instruct": True,
        "Baichuan2-7B-Chat": True,
        "Qwen2.5-0.5B": True
    },
    "ICL":{
        "ChatGLM3-6B": True,
        "Baichuan2-7B-Chat": True,
        "Chinese-Mistral-7B-Instruct-v0.1": True,
        "Mistral-7B-Instruct-v0.2": True,
        "Qwen2.5-0.5B": True,
        "Qwen1.5-7B-Chat": True,
        "Meta-Llama-3-8B-Instruct": True,
        "GLM-4-9B-Chat": True,
    },
    "Align":{
        "Chinese-Mistral-7B-Instruct-v0.1": True,
    },
    "MyMethod":{
        "Chinese-Mistral-7B-Instruct-v0.1": True,
        "Naive Align Edit Distance": True,
        "Perfect": True,
        "Naive Align Similarity": True
    }
})

R3_ALL_METHODS = OrderedDict({
    "Gold" : {
        "Gold_Query": False
    },
    "N3":{
        "GPT-4": False
    },
    "FT":{
        "Chinese-Mistral-7B-Instruct-v0.1": True,
        'ChatGLM3-6B': True,
        'Baichuan2-7B-Chat': True,
        'Qwen2.5-0.5B': True,
        'Mistral-7B-Instruct-v0.2': True,
        'Meta-Llama-3-8B-Instruct': True,
        'Qwen1.5-7B-Chat': True
    },
    "Align":{
        "Chinese-Mistral-7B-Instruct-v0.1": True,
    },
    "MyMethod":{
        "Perfect_Aligned_Intention": True,
        "Non_Aligned_Intention": True
    }
})