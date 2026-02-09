import os
from fpdf import FPDF
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random

from models import AcademicSource
from settings import settings

# Database setup
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_pdf(title, content, output_dir="/app/generated_papers"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)

    # Add content
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=content)
    
    file_path = os.path.join(output_dir, f"{title.replace(' ', '_').lower()}.pdf")
    pdf.output(file_path)
    print(f"Generated PDF: {file_path}")

def generate_plagiarized_paper_1(sources):
    """
    Generates a plagiarized paper by combining text from two different sources.
    """
    source1, source2 = random.sample(sources, 2)
    
    title = f"Plagiarized Paper 1: A Mix of {source1.title[:10]} and {source2.title[:10]}"
    
    content = f"This paper discusses a variety of topics, drawing heavily from existing literature.\n\n"
    content += f"--- Start of plagiarized section from '{source1.title}' ---\n\n"
    content += source1.full_text[:len(source1.full_text)//2]
    content += f"\n\n--- End of plagiarized section ---\n\n"
    content += f"--- Start of plagiarized section from '{source2.title}' ---\n\n"
    content += source2.full_text[len(source2.full_text)//2:]
    content += f"\n\n--- End of plagiarized section ---\n\n"
    
    create_pdf(title, content)

def generate_plagiarized_paper_2(sources):
    """
    Generates a plagiarized paper by taking text from one source and slightly modifying it.
    """
    source = random.choice(sources)
    
    title = f"Plagiarized Paper 2: Based on {source.title[:20]}"
    
    original_text = source.full_text
    modified_text = original_text.replace(" a ", " a new ")
    modified_text = modified_text.replace(" the ", " this particular ")
    
    content = f"This paper explores a well-established topic, building upon the work of others.\n\n"
    content += f"--- Start of plagiarized and modified section from '{source.title}' ---\n\n"
    content += modified_text
    content += f"\n\n--- End of section ---\n\n"
    
    create_pdf(title, content)

def generate_original_paper():
    """
    Generates an original paper on a new topic.
    """
    title = "An Original Paper on the Ethics of AI in Art"
    
    content = """
    The intersection of artificial intelligence and art has sparked a fascinating and complex ethical debate. 
    As AI algorithms become increasingly capable of generating novel creative works, questions surrounding authorship, 
    originality, and the very definition of art have come to the forefront. This paper explores the ethical dimensions 
    of AI in the art world, examining the implications for artists, audiences, and the cultural landscape as a whole.

    One of the central ethical challenges is the question of authorship. When an AI model creates a piece of art, 
    who is the artist? Is it the programmer who designed the algorithm, the user who provided the prompt, or the AI 
    itself? This ambiguity challenges traditional notions of artistic creation and intellectual property.

    Another key issue is the potential for AI to devalue human creativity. If AI can produce art that is 
    indistinguishable from or even superior to human-made art, what does this mean for the role of the human artist? 
    Some fear that AI could lead to a homogenization of artistic styles and a decline in the appreciation for the 
    skill and intentionality of human creators.

    However, there are also compelling arguments for the positive ethical implications of AI in art. AI can be a 
    powerful tool for artists, enabling them to explore new creative possibilities and push the boundaries of their 
    craft. It can also democratize art creation, making it more accessible to people who may not have traditional 
    artistic training.

    In conclusion, the integration of AI into the art world presents a host of ethical challenges and opportunities. 
    As this technology continues to evolve, it is crucial for artists, technologists, and the public to engage in a 
    thoughtful and ongoing dialogue about the ethical framework that should guide the creation and consumption of AI-generated art.
    """
    
    create_pdf(title, content)

if __name__ == "__main__":
    db = SessionLocal()
    try:
        academic_sources = db.query(AcademicSource).all()
        if len(academic_sources) < 2:
            print("Not enough academic sources in the database to generate plagiarized papers.")
            print("Please ingest at least 2 sources.")
        else:
            generate_plagiarized_paper_1(academic_sources)
            generate_plagiarized_paper_2(academic_sources)
            generate_original_paper()
    finally:
        db.close()
