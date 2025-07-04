from langchain.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

class LLMHandler:
    def __init__(self, model_name="llama3.1:8b-instruct-q4_0", temperature=0.1):
        self.llm = OllamaLLM(model=model_name, temperature=temperature)
        self.prompt = PromptTemplate.from_template("""
You are a helpful assistant analyzing computer usage logs.
Answer clearly and concisely in English based on the data below.


{context}


Respond to the user's question below with a short, direct answer only.


Question: {question}

""")

    def generate_response(self, context: str, question: str) -> str:
        try:
            response = (self.prompt | self.llm).invoke({
                "context": context,
                "question": question
            })

            if isinstance(response, str):
                for prefix in ["Answer:", "A:", "AI:", "Response:"]:
                    if prefix in response:
                        response = response.split(prefix)[-1].strip()
                return response.strip()

            return str(response)

        except Exception as e:
            print(f"❌ LLM error: {e}")
            return "Sorry, I couldn't answer your question right now."

    def generate_simple_response(self, prompt: str) -> str:
        return self.generate_response(context="", question=prompt)