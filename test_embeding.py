import os
import getpass
from dotenv import load_dotenv
from few_shots import few_shots

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import SemanticSimilarityExampleSelector, FewShotPromptTemplate, PromptTemplate
from langchain.chains.sql_database.prompt import PROMPT_SUFFIX
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables once
load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google API key: ")

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

to_vectorize = [" ".join(example.values()) for example in few_shots]

vectorstore = Chroma.from_texts(to_vectorize, embeddings, metadatas=few_shots)

example_selector = SemanticSimilarityExampleSelector(
    vectorstore=vectorstore,
    k=2,
)

mysql_prompt = """You are a MySQL expert. Given an input question, first create a syntactically correct MySQL query to run, then look at the results of the query and return JUST THE NUMERIC ANSWER.
Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per MySQL.
Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.
Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist.
Pay attention to use CURDATE() function to get the current date, if the question involves "today".

Use the following format:

Question: Question here
SQLQuery: Query to run with no pre-amble
SQLResult: Result of the SQLQuery
Answer: Just the numeric value from SQLResult

No pre-amble, no repetition of question or query in the Answer.
"""

example_prompt = PromptTemplate(
    input_variables=["Question", "SQLQuery", "SQLResult", "Answer"],
    template="\nQuestion: {Question}\nSQLQuery: {SQLQuery}\nSQLResult: {SQLResult}\nAnswer: {Answer}"
)

few_shot_prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix=mysql_prompt,
    suffix=PROMPT_SUFFIX,
    input_variables=["query", "table_info", "top_k"]
)

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

db_user = "root"
db_password = "root"
db_host = "localhost"
db_name = "atliq_tshirts"

db = SQLDatabase.from_uri(
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}",
    sample_rows_in_table_info=3
)

new_chain = SQLDatabaseChain.from_llm(
    llm, db, prompt=few_shot_prompt, verbose=True, use_query_checker=True
)

def run_query_and_get_answer(question, top_k=1):
    # Using invoke() instead of __call__ to avoid deprecation warning
    result = new_chain.invoke({
        "query": question,
        "table_info": db.get_table_info(),
        "top_k": top_k
    })
    
    # Extract just the numeric answer from the result
    if isinstance(result, dict) and 'result' in result:
        # Parse the chain output to get just the final answer
        answer_part = result['result'].split('Answer:')[-1].strip()
        return answer_part
    
    return result

question = "How many Adidas T shirts I have left in my store?"
answer = run_query_and_get_answer(question, top_k=1)

print("Final Answer:", answer)