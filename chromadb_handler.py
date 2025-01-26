import bs4
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from chromadb.utils import embedding_functions
import chromadb
import os
import uuid
import nltk
from nltk.chunk import ne_chunk
from nltk import Tree
import string
import spacy
import re
from termcolor import colored

class ChromadbHandler:
    def __init__(self, tool_objs: dict = None, tool_list: list = None, db_name="test_db_v1", collection_name="test_collection"):
        self.chroma_client = chromadb.PersistentClient(path=f"{os.getcwd()}/chroma_dbs/{db_name}")
        self.collection_name = collection_name
        self.embedding = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name, 
            embedding_function=self.embedding,
            metadata={
                "hnsw:space": "cosine",
                "hnsw:search_ef": 100
            }
        )
        self.tool_objs = tool_objs
        self.tools = tool_list


    def _create_doc_ids(self, documents):
        ids = []
        for _ in range(len(documents)):
            ids.append(str(uuid.uuid4()))
        return ids

    # Add new documents to the chromadb collection
    def add_docs_to_collection(self, documents, ids=None, metadata=None):
        # Create doc IDs if needed
        if ids is None:
            ids = self._create_doc_ids(documents)
        # Add documents to chromadb collection
        if metadata is None:
            self.collection.add(documents=documents, ids=ids)
        else:
            self.collection.add(documents=documents, metadatas=metadata, ids=ids)

    def add_test_data_to_collection(self, documents=None):
        ids = []
        documents = [
            "Artificial intelligence is the simulation of human intelligence processes by machines.",
            "Python is a programming language that lets you work quickly and integrate systems more effectively.",
            "ChromaDB is a vector database designed for AI applications. ChromaDB is commonly used for retrieval-augmented generation with LLMs.",
            "The Nuggets are an NBA team based in Denver, Colorado.",
            "The Broncos are an NFL team besed in Denver, Colorado.",
            "The Los Angeles Lakers are an NBA team based in Los Angeles, California.",
            "Ethereum's price has increased by 20 percent over the past week, following the bullish trend across the entire crypto market.",
            "The Orange Bowl is one of college football's largest bowl games. It is played in Miami, Florida every year.",
            "The Fort Worth stockyards are a historic landmark and tourist attraction near downtown Fort Worth, Texas."
        ]
        ids = self._create_doc_ids(documents)
        self.collection.add(documents=documents, ids=ids)

    def _truncate_url(self, url):
        tlds = [".com", ".org", ".net"]
        for i in range(len(tlds)):
            index = url.find(tlds[i])
            if index != -1:
                return url[:index + len(tlds[i])]
        return url

    def add_web_data_to_chromadb(self, url):
        splits = self.load_and_split_webpage(url)
        # ids = self._create_doc_ids(documents=splits)
        metadata_url = self._truncate_url(url)
        metadata = [{"source": metadata_url} for _ in range(len(splits))]
        # self.collection.add(documents=splits, metadatas=metadata, ids=ids)
        self.add_docs_to_collection(documents=splits, metadata=metadata)

    def _get_connected_nouns(self, tags, query_nouns):
        i = 0
        while i<len(tags) and i >= 0:
            w, pos = tags[i]
            if pos not in ['NN', 'NNP', 'NNS']:
                i += 1
                continue
            elif i<len(tags)-1:
                np = []
                np_end = -1
                for j in range(i, len(tags)):
                    wj, posj = tags[j]
                    if posj in ['NN', 'NNP', 'NNS']:
                        np.append(wj)
                    elif len(np) > 1:
                        query_nouns.append(" ".join(np))
                        np_end = j
                        break
                    else:
                        np_end = j
                        break
                i = np_end
            else:
                i+=1
        return query_nouns
    
    def _get_noun_chunks(self, tags, query_nouns):
        chunks = ne_chunk(tags)
        continuous_chunk = []
        current_chunk = []
        for subtree in chunks:
            if type(subtree) == Tree:
                current_chunk.append(" ".join([token for (token, pos) in subtree.leaves()]))
            elif current_chunk:
                named_entity = " ".join(current_chunk)
                if named_entity not in continuous_chunk:
                    continuous_chunk.append(named_entity)
                    current_chunk = []
            else:
                continue
        for np in continuous_chunk:
            if np not in query_nouns:
                query_nouns.append(np)
        return query_nouns

    def _get_query_nouns(self, query_text):
        tokens = nltk.word_tokenize(query_text)
        tags = nltk.pos_tag(tokens)
        query_nouns = [w for (w, pos) in tags if pos in ['NN', 'NNP', 'NNS']]
        # print(f"Nouns: {query_nouns}")
        query_nouns = self._get_connected_nouns(tags, query_nouns)
        # print(f"Nouns After Loop: {query_nouns}")
        query_nouns = self._get_noun_chunks(tags, query_nouns)
        # print(f"Final Nouns: {query_nouns}")
        return query_nouns

    def query_chromadb(self, query_text, n_results=4):
        # Get potentially relevant documents from chromadb
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        # Get similarities of results returned from chromadb query
        print("\n######## Query Results ########")
        distances = []
        for i in range(len(results['documents'][0])):
            print(f"{results['documents'][0][i][:15]}...:: {results['distances'][0][i]}") 
            distances.append(results['distances'][0][i])
        # Get nouns contained in user query
        # query_nouns = self._get_query_nouns(query_text)
        # print(f"Q NOUNS :: {query_nouns}")

        # Get nouns contained in each sentence of the query
        end_sent = "\.|!|\?"
        query_sents = re.split(end_sent, query_text)
        sent_nouns = []
        for s in query_sents:
            q_nouns = self._get_query_nouns(s)
            if len(q_nouns) > 0:
                sent_nouns.append(q_nouns)

        # Determine if returned documents are relevant to the user's query
        lowest_distance = distances[0]
        collected_docs = []
        noun_count = 0
        translator = str.maketrans('', '', string.punctuation)
        for sn in sent_nouns:
            # Loop through all returned documents
            for i in range(len(results['documents'][0])):
                noun_count = 0
                current_text = results['documents'][0][i]
                # Only loop until similarity score is 20% > the lowest score
                if distances[i] < lowest_distance*1.2:
                    # Format the document text and store in an array
                    doc_text = current_text.lower()
                    doc_text = doc_text.replace("'s", "")
                    cleaned_doc_text = doc_text.translate(translator)
                    current_doc = cleaned_doc_text.split(" ")
                    # Check if the number of nouns in both the query and the text meets the threshold
                    for n in sn:
                        if n.lower() in current_doc:
                            noun_count += 1
                    if results['distances'][0][i] <= 0.4:
                        threshold = max(1, round(len(sn)*results['distances'][0][i]))
                    elif results['distances'][0][i] > 0.4:
                        threshold = round(len(sn)*max(0.75, results['distances'][0][i]))
                    print(f"Len = {len(sn)}  :::  Noun Count = {noun_count}  :::  Threshold = {threshold}")
                    if noun_count >= threshold and current_text not in collected_docs:
                        print(f"Adding CONTEXT WITH :: Len = {len(sn)}  :::  Noun Count = {noun_count}  :::  Threshold = {threshold}")
                        collected_docs.append(current_text)
                else:
                    break
        # Return the results of chromadb query
        if len(collected_docs) > 0:
            return " ".join(collected_docs)
        else:
            return None

        
    def query_tools(self, query_text, n_results=1):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results['documents'][0][0]
    
    
    def get_rag_prompt(self, query_text):
        retrieved_docs = self.query_chromadb(query_text)
        if retrieved_docs is not None:
            augmented_prompt = f"Question: {query_text}\n\nContext: {retrieved_docs}"
        else:
            augmented_prompt = f"Question: {query_text}"
        return {"role": "user", "content": augmented_prompt}
    

    def load_and_split_webpage(self, url):
        # Create loader for web page 
        loader = WebBaseLoader(
            web_paths=(url,),
            bs_kwargs=dict(parse_only=bs4.SoupStrainer("p"))
        )
        # Load and split web page content
        docs = loader.load()
        print(f"\n\nDOCS--\n{docs}")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        print(f"\n\SPLITS--\n{splits}")
        str_splits = [split.page_content for split in splits]
        return str_splits
    
    def delete_doc(self, ids):
        self.collection.delete(ids=ids)

    def delete_tool(self, tool):
        id = [tool.name]
        self.delete_doc(ids=id)

    def add_tool(self, tool):
        name = tool.name
        doc = [tool.description]
        id = [name]
        metadata = [{"tool_name": name}]
        self.add_docs_to_collection(documents=doc, ids=id, metadata=metadata)

    def get_tool_prompt(self, tool_response, prompt, rag_prompt):
        tool_calls = tool_response["message"]["tool_calls"]
        tool_data = []
        for t in tool_calls:
            tool_name = t["function"]["name"]
            tool_desc = self.tool_objs[tool_name].description
            retrieved_desc = self.query_tools(query_text=prompt)
            if retrieved_desc == tool_desc:
                print(f"\n{colored('MATCHING TOOL FOUND', 'green')}\nDescription :: {tool_desc}")
                print("Type 'y' to use the tool. Otherwise, the tool will not be called.")
                use_tool = input("Use Tool: ")
                if use_tool == "y":
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