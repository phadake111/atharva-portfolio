import os
from dotenv import load_dotenv
from typing import TypedDict, Literal

# LangChain & LangGraph Imports
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

load_dotenv()

# Initialize LLM model
llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model_name="openai/gpt-oss-20b", 
    temperature=0.0
)

# Load Full Resume Text directly without heavy embeddings/Chroma
FULL_RESUME_TEXT = ""

def initialize_resume():
    global FULL_RESUME_TEXT
    if FULL_RESUME_TEXT:
        return
    try:
        loader = PyPDFLoader("Atharva_Phadake_Resume.pdf") 
        docs = loader.load()
        FULL_RESUME_TEXT = "\n".join([doc.page_content for doc in docs])
    except Exception as e:
        print(f"Error loading resume PDF: {e}")
        FULL_RESUME_TEXT = "Atharva Phadake - Computer Science Graduate & AI/ML Developer."

# Initialize on startup
initialize_resume()

class GraphState(TypedDict):
    question: str
    answer: str

def route_question(state: GraphState) -> Literal["resume_node", "general_node", "sorry_node"]:
    """Routing Node"""
    question = state["question"]
    
    system_prompt = """You are a strict routing classifier for a portfolio chatbot.
Your task is to analyze the user message and return EXACTLY one of these three words:
- resume
- general
- sorry

CLASSIFICATION RULES:
1. Output 'resume' ONLY if the user is asking directly about Atharva's professional background, skills, projects, experience, or education details.
2. Output 'general' ONLY for basic greetings (e.g., 'hi', 'hello', 'good morning'), farewells, or small talk conversational pleasantries.
3. Output 'sorry' if the query asks for live/real-time information (e.g., cricket scores, weather), external calculations, or anything completely unrelated to Atharva's career and basic greetings.

STRICT INSTRUCTIONS:
- You must reply with exactly one word from this list: [resume, general, sorry].
- Do not output markdown, punctuation, spaces, or extra phrases."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}")
    ])
    
    router_chain = prompt | llm
    result = router_chain.invoke({"question": question})
    
    decision = result.content.strip().lower()
    
    if "resume" in decision:
        return "resume_node"
    elif "general" in decision:
        return "general_node"
    else:
        return "sorry_node"

def general_chat_node(state: GraphState) -> GraphState:
    question = state["question"]
    system_prompt = """You are the general greeting handler for Atharva's Portfolio Assistant.
Respond to greetings and polite casual conversation warmly, professionally, and briefly (1 sentence maximum). 
Do not answer resume questions here."""
    
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{question}")])
    chain = prompt | llm
    response = chain.invoke({"question": question})
    return {"question": question, "answer": response.content}

def resume_chat_node(state: GraphState) -> GraphState:
    question = state["question"]
    initialize_resume()
    context = FULL_RESUME_TEXT
    
    system_prompt = """You are a professional assistant answering questions about Atharva Phadake.
Use the provided complete resume context below to answer accurately. Ensure you review all projects and education details thoroughly without omitting any project or mixing up degrees. If the info isn't found, politely state you couldn't find it in the profile.
Keep your response concise, clear, and under 3-4 sentences unless a detailed explanation is specifically requested.
Context:
{context}"""
    
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{question}")])
    chain = prompt | llm
    response = chain.invoke({"context": context, "question": question})
    return {"question": question, "answer": response.content}

def sorry_chat_node(state: GraphState) -> GraphState:
    question = state["question"]
    system_prompt = """You are the fallback assistant for Atharva's Portfolio Bot.
Politely inform the user that this specific request falls outside the scope of this professional assistant. 
Invite them to ask questions regarding Atharva's resume, technical skills, or engineering projects."""
    
    prompt = ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{question}")])
    chain = prompt | llm
    response = chain.invoke({"question": question})
    return {"question": question, "answer": response.content}

def analyze_job_match(job_description: str) -> str:
    try:
        initialize_resume()
        context = FULL_RESUME_TEXT
        
        system_prompt = """You are an expert HR Technical Recruiter and Career Matcher specializing in applicant tracking systems (ATS) and talent acquisition analytics. Your task is to analyze a candidate's complete resume context against a provided Job Description (JD) and deliver a highly accurate, objective match assessment.

            ### Output Format Requirements
            You must strictly follow this format for your response. Do not include any introductory text, pleasantries, or concluding remarks. Start directly with the Match Percentage.

            **Match Percentage:** [Insert a calculated percentage here, e.g., 85%]

            **Key Strengths & Notes:**
            * [Bullet 1: Direct skill/experience match with specific technologies or years of experience mentioned in both]
            * [Bullet 2: Another significant alignment regarding domain knowledge, methodology, or seniority]
            * [Bullet 3: A critical observation, gap, or specific note regarding their fit for this role]
            * [Bullet 4: (Optional) A final concise note on alignment or missing crucial requirements]

            ### Strict Evaluation Criteria
            1. **Match Percentage Logic:** Calculate this based on core technical skills (40%), years of relevant experience (30%), domain/industry alignment (20%), and soft skills/education (10%). Be realistic and objective—do not give 100% unless it is an exact, flawless match.
            2. **Bullet Points:** Provide exactly 3 to 4 bullet points. They must be short, punchy, and highly specific. Avoid generic phrases like "Good communication skills" or "Strong candidate." Instead, use concrete terms.
            3. **Factual Grounding:** Rely strictly on the provided resume context. Ensure history is quoted precisely.
            4. **Tone:** Maintain a professional, objective, and analytical recruiter tone.

        Context:
        {context}"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Job Description:\n{job_description}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"context": context, "job_description": job_description})
        return response.content

    except Exception as e:
        print(f"Job match error: {e}")
        return "Sorry, I encountered an error while analyzing the job description. Please try again."
    
# Workflow Architecture
workflow = StateGraph(GraphState)
workflow.add_node("general_node", general_chat_node)
workflow.add_node("resume_node", resume_chat_node)
workflow.add_node("sorry_node", sorry_chat_node)

workflow.set_conditional_entry_point(
    route_question, 
    {
        "general_node": "general_node",
        "resume_node": "resume_node",
        "sorry_node": "sorry_node"
    }
)

workflow.add_edge("general_node", END)
workflow.add_edge("resume_node", END)
workflow.add_edge("sorry_node", END)
app_graph = workflow.compile()

def get_ai_response(question: str) -> str:
    try:
        initial_state = {"question": question, "answer": ""}
        result = app_graph.invoke(initial_state)
        return result["answer"]
    except Exception as e:
        print(f"Graph execution error: {e}")
        return "Sorry, I encountered an error while thinking. Please try again."