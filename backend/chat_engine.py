import os
from optimum.onnxruntime import ORTModelForCausalLM
from transformers import AutoTokenizer

class ChatEngine:
    def __init__(self, model_dir="onnx_chat_model"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = ORTModelForCausalLM.from_pretrained(
            model_dir,
            file_name="model_int8.onnx",
            provider="CPUExecutionProvider",
            use_cache=True
            )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def format_prompt(self,messages):
        return self.tokenizer.apply_chat_template(
            messages,
            tokenize = False,
            add_generation_prompt = True
        )

    def generate_response(self,messages,max_new_tokens=128,temperature=0.7):
        prompt_text = self.format_prompt(messages)
        input = self.tokenizer(prompt_text,return_tensors="pt")

        do_sample = temperature > 0.0
        output_ids = self.model.generate(
            **input,
            max_new_tokens=max_new_tokens,
            do_sample=do_sample,
            temperature=temperature if do_sample else None,
            pad_token_id=self.tokenizer.pad_token_id,
            eos_token_id=self.tokenizer.eos_token_id
            )

        input_len = input["input_ids"].shape[1]
        generated_tokens = output_ids[0][input_len:]

        reply = self.tokenizer.decode(generated_tokens,skip_special_tokens=True)
        return reply.strip()

if __name__ == "__main__":
    eng = ChatEngine(model_dir="onnx_chat_model")
    sample_dialogue = [
        {"role":"system","content":"you are a concise IT support agent."},
        {"role":"user","content":"How do I check my IP address in terminal?"}
    ]
    print(eng.generate_response(sample_dialogue,max_new_tokens=64))