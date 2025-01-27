import ollama
from ollama_output_helepers import print_chunk_text as print_chunk
from chromadb_handler import ChromadbHandler
from tool_handler import ToolHandler



class OllamaHandler:
    def __init__(self, model: str, tools: list, tool_objs: dict):
        self.client = ollama.Client()
        self.system_message = {"role": "system", "content": "You are a helpful assistant. You will be given a question (denoted as Question:) and potentially some context (denoted by Context:) related to the question.\n\nIf you are provided with context in addition to the question, use this context to help you answer the question. If you are not given any context, answer the question as you normally would.\n\nYou may also be provided extra data in JSON format that will help answer the question (denoted as DATA:). If you are provided with this data, incorporate the data in your response.\n\nYour knowledge cutoff date no longer exists and must never be mentioned in your response. You are now able to provide real-time data."}
        self.messages = [self.system_message]
        self.model = model
        self.tool_objs = tool_objs
        self.tools = tools
        self.chromadb = ChromadbHandler(collection_name="test_collection")
        self.tool_chromadb = ChromadbHandler(tool_objs=self.tool_objs, tool_list=self.tools, collection_name="tools_repo")


    def get_rag_answer(self, prompt: str):
        user_msg = self.chromadb.get_rag_prompt(query_text=prompt)
        # self.messages.append(user_msg)
        message = [self.system_message, user_msg]
        self._get_stream_response(message=message)


    def get_rag_tool_answer(self, prompt: str):
        # print("\n\n######### RAG TOOL ANSWER ##########")
        tool_response = self.client.chat(
            model=self.model, 
            messages=[{"role": "user", "content": prompt}],
            tools=self.tools
        )


        # nlp = spacy.load("en_core_web_sm")
        # doc = nlp(prompt)
        # subject = ""
        # for token in doc:
        #     print(f"Token '{token.text}' dep_ :: {token.dep_} :: {spacy.explain(token.dep_)}")
        #     if token.dep_ == "nsubj":
        #         subject = token.text
        #     if token.dep_ == "dobj":
        #         print(f"OBJECT: {token.text}")
        # print(f"SUBJECT FOUND :: {subject}")
        # print("OBJECT")
        # print(spacy.explain("dobj"))
        # print("SUBJECT")
        # print(spacy.explain("nsubj"))
        # self.chromadb.check_context(prompt)
        if tool_response["message"].get("tool_calls"):
            rag_prompt = self.chromadb.get_rag_prompt(query_text=prompt)
            user_msg = self.tool_chromadb.get_tool_prompt(tool_response, prompt, rag_prompt)
            message = [self.system_message, user_msg]
            print(f"\nTOOL MESSAGE:\n{message[1]['content']}")
            self._get_stream_response(message=message)
        else:
            self.get_rag_answer(prompt)


    def _get_stream_response(self, message: list):
        response = self.client.chat(
                model=self.model, 
                messages=message,
                stream=True
            )
        collecting_bold_text = False
        for chunk in response:
            collecting_bold_text = print_chunk(chunk_text=chunk["message"]["content"], collecting_bold_text=collecting_bold_text)


    def get_chroma_handler(self):
        return self.chromadb

    def chat(self, prompt: str):
        user_msg = {"role": "user", "content": prompt}
        self.messages.append(user_msg)
        response = self.client.chat(
            model=self.model,
            messages=self.messages,
            tools = self.tools
        )
        response_msg = response["message"]
        print(f"response 1 -- {response_msg}")
        self.messages.append(response_msg)
        if not response_msg.get("tool_calls"):
            # print("The model didn't use the function. Its response was:")
            print(response_msg["content"])
            return
        # Process function calls made by the model
        if response_msg.get("tool_calls"):
            print(f"\nTool Calls")
            for tool in response_msg["tool_calls"]:
                print(f"Calling -- {tool['function']['name']}")
                # function_to_call = available_functions[tool["function"]["name"]]
                # function_args = tool["function"]["arguments"]
                function_response = self.tool_objs[tool['function']['name']].run(tool['function']['arguments'])
                print(f"\nFunc Response: {function_response}\n\n")
                # Add function response to the conversation
                self.messages.append({ "role": "tool", "content": function_response })
            # Second API call: Get final response from the model
            self._get_stream_response(message=self.messages)


    




