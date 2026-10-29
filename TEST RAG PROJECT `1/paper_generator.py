
def ask_ai(client, model, prompt):
    """OpenRouter se text response leta hai."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful educational assessment "
                    "assistant. Follow the user's instructions "
                    "and never claim a practice paper is official."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("AI ne empty response diya.")

    return content.strip()


def generate_paper(client, model, settings, pdf_context):
    """Complete practice paper aur optional answer key generate karta hai."""

    prompt = f"""
Create a complete educational PRACTICE question paper.

BOARD: {settings['board']}
CLASS: {settings['class_name']}
SUBJECT: {settings['subject']}
LANGUAGE: {settings['language']}
DIFFICULTY: {settings['difficulty']}
DURATION: {settings['duration']} minutes
USER'S TARGET MARKS: {settings['total_marks']}

MCQ COUNT: {settings['mcq_count']}
MARKS PER MCQ: {settings['mcq_marks']}

SHORT QUESTIONS TO INCLUDE: {settings['short_count']}
SHORT QUESTIONS TO ATTEMPT: {settings['short_attempt']}
MARKS PER SHORT QUESTION: {settings['short_marks']}

LONG QUESTIONS TO INCLUDE: {settings['long_count']}
LONG QUESTIONS TO ATTEMPT: {settings['long_attempt']}
MARKS PER LONG QUESTION: {settings['long_marks']}

ADDITIONAL TOPICS:
{settings['topics'] or 'Use the supplied PDF content.'}

CUSTOM INSTRUCTIONS:
{settings['instructions'] or 'No extra instructions.'}

RULES:
1. Use the PDF context as the primary source when provided.
2. Include the additional topics where relevant.
3. If no PDF context is supplied, use the given topics and
   appropriate subject knowledge without claiming the content
   came from a PDF.
4. Generate the exact requested number of each question type.
5. Each MCQ must have four options labelled A, B, C and D,
   with one best answer.
6. Clearly show section headings, question numbers and marks.
7. Do not include answers in the question paper.
8. Clearly state how many short and long questions students
   must attempt.
9. Calculate actual maximum marks from the attempt rules.
   MCQ marks = MCQ count x marks per MCQ.
   Short marks = short questions to attempt x marks per question.
   Long marks = long questions to attempt x marks per question.
10. If the calculated marks differ from the user's target,
    show the actual calculated marks and a brief note.
11. Do not claim that this is the latest official Sindh Board
    examination pattern unless an official scheme is supplied.
12. Keep the paper readable and suitable for printing.
13. Write the paper in the requested language.

PDF CONTEXT:
{pdf_context[:20000] if pdf_context else 'No PDF context supplied.'}

Return only the question paper in Markdown.
"""

    paper = ask_ai(client, model, prompt)

    answer_key = ""

    if settings.get("include_key", True):
        answer_prompt = f"""
Create a separate teacher's answer key for this practice paper.

SUBJECT: {settings['subject']}
CLASS: {settings['class_name']}
LANGUAGE: {settings['language']}

Instructions:
- Keep exactly the same question numbering and sections.
- Give the correct option and answer for each MCQ.
- Give suggested model answers or marking points for short
  and long questions.
- Use the PDF context when relevant.
- Flag uncertain answers for teacher review.
- Do not invent unsupported facts.
- Return only the answer key in Markdown.

PDF CONTEXT:
{pdf_context[:12000] if pdf_context else 'No PDF context supplied.'}

QUESTION PAPER:
{paper[:22000]}
"""

        answer_key = ask_ai(
            client,
            model,
            answer_prompt
        )

    return paper, answer_key
