from chromadb_handler import ChromadbHandler

class ToolHandler:
    def __init__(self, tool_objs: dict, tool_desc: list, collection_name="tools_repo", ):
        self.collection_name = collection_name
        self.chromadb = ChromadbHandler(collection_name=self.collection_name)
        self.tool_objs = tool_objs
        self.tool_desc = tool_desc

    def add_tool_to_chromadb(self, tool):
        name = tool.name
        doc = [tool.description]
        id = [name]
        metadata = [{"tool_name": name}]
        self.chromadb.add_docs_to_collection(documents=doc, ids=id, metadata=metadata)

    def delete_tool_from_chromadb(self, tool):
        id = [tool.name]
        self.chromadb.delete_doc(ids=id)

    def query_tools(self, query_text):
        retrieved_tool_description = self.chromadb.query_tools(query_text)
        return retrieved_tool_description
    
    def get_tool_prompt(self, tool_response, prompt, rag_prompt):
        tool_calls = tool_response["message"]["tool_calls"]
        tool_data = []
        for t in tool_calls:
            tool_name = t["function"]["name"]
            tool_desc = self.tool_objs[tool_name].description
            retrieved_desc = self.query_tools(query_text=prompt)
            if retrieved_desc == tool_desc:
                print(f"MATCHING TOOL FOUND WITH DESC: {tool_desc}")
                tool_response = self.tool_objs[tool_name].run(t["function"]["arguments"])
                tool_data.append(tool_response)
        ###############
        # TODO: Simplify redundant code
        ###############
        tool_data_str = ""
        if len(tool_data) > 0:
            for d in tool_data:
                tool_data_str += d if len(tool_data_str)==0 else f", {d}"
            return {"role": "user", "content": f"{rag_prompt['content']}\n\nDATA: {tool_data_str}"}
        else:
            return rag_prompt