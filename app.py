import streamlit as st
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from typing import TypedDict
from pydantic import BaseModel, Field
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
import re
from google import genai
from fpdf import FPDF

# Load environment variables (ensure you set GOOGLE_API_KEY in .env)
load_dotenv()

# Define schema and state
class schema(BaseModel):
    summary: str = Field(description="Summary of the video")

class rstate(TypedDict):
    url: str
    transcript: str
    summary: str 
    note:str
import re
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

# Function: Extract transcript (Updated with your provided method)
def get_transcript_from_url(state: rstate) -> rstate:
    """Extracts a transcript from a YouTube URL using the .fetch() method
    with language fallback and preserved formatting."""
    
    # Extract video ID using regex
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", state["url"])
    if not match:
        raise ValueError("Invalid YouTube URL or video ID not found.")
    
    video_id = match.group(1)

    try:
        # Create an instance of the API
        ytt_api = YouTubeTranscriptApi()

        # Fetch the transcript using your specified method.
        # It tries Hindi ('hi') first, then English ('en').
        # It also preserves formatting like bold or italics.
        fetched_transcript = ytt_api.fetch(
            video_id, 
            languages=['hi', 'en'], 
            preserve_formatting=True
        )

        # Join all text parts from the iterable snippets into one string
        full_transcript = " ".join([snippet.text for snippet in fetched_transcript])
        
        return {"transcript": full_transcript}

    except NoTranscriptFound:
        # Handle cases where no transcript is available in the specified languages
        raise Exception(f"No transcript found for video ID '{video_id}' in Hindi or English.")
    except Exception as e:
        # Catch other potential errors
        raise e# Function: Summarize transcript using Gemini
def summarize_transcript(state: rstate) -> rstate:
    client = genai.Client()
    
    prompt = f"Here is a full transcript of a YouTube video:\n\n{state['transcript']}\n\nPlease provide a detailed summary of the content."
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return {"summary": response.text}

# for the notes
def notes(state: rstate) -> rstate:
    client = genai.Client()
    
    prompt = f"""ROLE: You are an expert academic assistant specializing in distilling complex information into clear, concise, and effective study materials.

TASK: Your goal is to transform the following YouTube video transcript into a comprehensive set of exam study notes. You must identify the core educational content, structure it logically, and present it in a way that is optimized for learning and revision.

INSTRUCTIONS:

Analyze the entire transcript to understand the main topics, key concepts, and the overall flow of information.

Filter out all non-essential content. This includes conversational filler (e.g., "um," "ah," "you know"), personal anecdotes unless they are a core part of an example, and any sponsorship messages or calls to action (e.g., "like and subscribe").

Generate the notes using the following structured format:

## 📝 Main Title: Create a clear, descriptive title for the notes based on the video's subject.

## 💡 Key Takeaways (TL;DR): Start with a bulleted list of 3-5 of the most crucial points or conclusions from the video. This is for quick review.

## 📚 Detailed Notes:

Organize the main content using clear headings and subheadings.

Use bullet points or numbered lists for supporting details, steps in a process, or examples.

Bold all key terms, definitions, and important names/dates.

Explain complex topics in simple terms. If the video uses an analogy, include it. If not, create a simple one to aid understanding.

## 🔑 Key Definitions & Terminology:

Create a dedicated section listing all the important vocabulary from the video.

Format it as: Term: Definition.

## 🧪 Formulas / Equations (if applicable):

If the video contains any mathematical formulas, scientific equations, or code snippets, list them here.

Use LaTeX formatting for all mathematical notations (e.g., $E=mc^2$).

Briefly explain what each variable in the formula represents.

## 🤔 Potential Exam Questions:

Based on the content, generate 3-4 potential exam questions (e.g., multiple-choice, short answer, or conceptual questions) to help test understanding. Provide a brief answer for each.

Final Output Style:

Use clear and concise language.

The tone should be educational and straightforward.

Employ markdown formatting extensively to ensure the notes are well-organized and easy to read.

{state['transcript']}
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return {"note":response.text}

# Build LangGraph workflow
graph = StateGraph(rstate)
graph.add_node("get_transcript_from_url",get_transcript_from_url)
graph.add_node("summarize_transcript",summarize_transcript)
graph.add_node("notes",notes)

graph.add_edge(START,"get_transcript_from_url")
graph.add_edge("get_transcript_from_url","summarize_transcript")
graph.add_edge("get_transcript_from_url","notes")
graph.add_edge("summarize_transcript",END)

workflow = graph.compile()

from fpdf import FPDF

# ---------------- Streamlit App ----------------
st.title("🎥 YouTube Video Summarizer + Notes")
st.write("Paste a YouTube link to get the transcript, summary, and study notes.")

url = st.text_input("Enter YouTube Video URL:")

if st.button("Process Video"):
    if url.strip() == "":
        st.warning("Please enter a valid YouTube URL.")
    else:
        with st.spinner("Fetching transcript and generating content..."):
            try:
                result = workflow.invoke({"url": url})

                # Store results in session state
                st.session_state["transcript"] = result["transcript"]
                st.session_state["summary"] = result["summary"]
                st.session_state["note"] = result["note"]

                st.success("Processing completed! Use the buttons below to view.")

            except Exception as e:
                st.error(f"Error: {e}")

# Buttons to reveal content (stacked vertically)
if "transcript" in st.session_state:
    if st.button("📜 Show Transcript"):
        st.subheader("Transcript")
        st.text_area("Full Transcript", st.session_state["transcript"], height=300)

if "summary" in st.session_state:
    if st.button("📝 Show Summary"):
        st.subheader("Summary (AI)")
        st.write(st.session_state["summary"])

if "note" in st.session_state:
    if st.button("📖 Show Study Notes"):
        st.subheader("Study Notes")
        st.markdown(st.session_state["note"])

        # Create PDF with Unicode font
        
        pdf = FPDF()
        pdf.add_page()

        # Add Unicode font (DejaVuSans.ttf should be in the same folder)
        pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVu", "", 12)

        pdf.multi_cell(0, 10, st.session_state["note"])

        pdf_output = "study_notes.pdf"
        pdf.output(pdf_output)

        # Download button
        with open(pdf_output, "rb") as f:
            st.download_button(
                label="⬇️ Download Notes as PDF",
                data=f,
                file_name="study_notes.pdf",
                mime="application/pdf"
            )