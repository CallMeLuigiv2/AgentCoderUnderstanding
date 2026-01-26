from mistral_common.tokens.tokenizers.mistral import MistralTokenizer

def get_tokenizer(model: str):
    """
    Returns the appropriate Mistral tokenizer version based on the model name.
    Supports: ministral-3:8b-instruct-2512-q4_K_M
    """
    model_name = model.lower()
    try:
        # Check for the specific V3/Ministral family (Dec 2025 release)
        if any(key in model_name for key in ["v3", "ministral", "2512"]):
            return MistralTokenizer.v3()
        
        elif "v2" in model_name:
            return MistralTokenizer.v2()
            
        else:
            return MistralTokenizer.v1()
            
    except Exception as e:
        # Combined Fallback: Keeps the agent running if loading fails
        print(f"Warning: Could not load tokenizer for {model} ({e}). Falling back to V3.")
        return MistralTokenizer.v3()

def count_tokens(text: str, model: str) -> int:
    tokenizer = get_tokenizer(model)

    if tokenizer:
        tokens = tokenizer.instruct_tokenizer.tokenizer.encode(text, bos=False, eos=False)
        return len(tokens)

    return estimate_tokens(text, model)

def estimate_tokens(text: str, model: str) -> int:

    return max(1,len(text)//4)