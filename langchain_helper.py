import os
import re
import asyncio
from decimal import Decimal
from dotenv import load_dotenv
from few_shots import few_shots
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import SemanticSimilarityExampleSelector, FewShotPromptTemplate, PromptTemplate
from langchain.chains.sql_database.prompt import PROMPT_SUFFIX
from langchain_community.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain_google_genai import ChatGoogleGenerativeAI

class TShirtQueryHelper:
    def __init__(self):
        load_dotenv()
        self.embeddings = self._init_embeddings()
        self.vectorstore = self._init_vectorstore()
        self.db = self._init_database()
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        self.chain = self._create_chain()
    
    def _init_embeddings(self):
        try:
            return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        except RuntimeError as e:
            if "no current event loop" in str(e):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
            raise
    
    def _init_vectorstore(self):
        return Chroma.from_texts(
            [" ".join(example.values()) for example in few_shots],
            self.embeddings,
            metadatas=few_shots
        )
    
    def _init_database(self):
        return SQLDatabase.from_uri(
            f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}",
            sample_rows_in_table_info=3,
            include_tables=['t_shirts', 'discounts']  # Explicitly include relevant tables
        )
    
    def _create_chain(self):
        example_selector = SemanticSimilarityExampleSelector(
            vectorstore=self.vectorstore,
            k=2,
        )

        mysql_prompt = """You are a MySQL expert. Given an input question, first create a syntactically correct MySQL query to run, then look at the results of the query and return the answer to the input question.
    Unless the user specifies in the question a specific number of examples to obtain, query for at most {top_k} results using the LIMIT clause as per MySQL. You can order the results to return the most informative data in the database.
    Never query for all columns from a table. You must query only the columns that are needed to answer the question. Wrap each column name in backticks (`) to denote them as delimited identifiers.
    Pay attention to use only the column names you can see in the tables below. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    Pay attention to use CURDATE() function to get the current date, if the question involves "today".
    
    Use the following format:
    
    Question: Question here
    SQLQuery: Query to run with no pre-amble
    SQLResult: Result of the SQLQuery
    Answer: Final answer here
    
    No pre-amble.
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

        return SQLDatabaseChain.from_llm(
            self.llm, 
            self.db, 
            prompt=few_shot_prompt,
            verbose=True,
            use_query_checker=True,
            return_intermediate_steps=True
        )


    def query_tshirt_inventory(self, question, top_k=1):
        try:
            cleaned_question = re.sub(r'```sql\s*|\s*```', '', question).strip()
            
            result = self.chain.invoke({
                "query": cleaned_question,
                "table_info": self.db.get_table_info(),
                "top_k": top_k
            })
            
            def clean_sql_query(sql):
                """Remove markdown code blocks and clean the SQL query"""
                sql = re.sub(r'^```sql\s*|```\s*$', '', sql, flags=re.IGNORECASE)
                sql = sql.strip()
                sql = ' '.join(sql.split())
                return sql

            def format_numeric_answer(value):
                try:
                    if isinstance(value, (Decimal, float, int)):
                        return float("{:.2f}".format(float(value)))
                    elif isinstance(value, str):
                        cleaned = re.sub(r'[^\d.-]', '', value)
                        if cleaned:
                            return float("{:.2f}".format(float(cleaned)))
                    return value
                except:
                    return value

            if isinstance(result, dict) and 'intermediate_steps' in result:
                for step in result['intermediate_steps']:
                    if 'sql_query' in step and step['sql_query']:
                        step['sql_query'] = clean_sql_query(step['sql_query'])
                    
                    if 'sql_result' in step and step['sql_result']:
                        sql_result = step['sql_result']
                        if sql_result and len(sql_result) > 0 and len(sql_result[0]) > 0:
                            return format_numeric_answer(sql_result[0][0])
            
            if isinstance(result, dict) and 'result' in result:
                answer_part = result['result'].split('Answer:')[-1].strip()
                return format_numeric_answer(answer_part)
            
            if isinstance(result, (Decimal, float, int)):
                return format_numeric_answer(result)
            
            if isinstance(result, str):
                return format_numeric_answer(result)
            
            return result
            
        except Exception as e:
            return f"Error processing query: {str(e)}"