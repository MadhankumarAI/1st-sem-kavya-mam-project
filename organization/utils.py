import random
import string
from django.core.mail import send_mail
from django.conf import settings


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code):
    subject = 'Your Verification Code'
    message = f'Your verification code is: {code}\nThis code will expire in 30 seconds.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
def send_reset_code_email(email, code):
    subject = 'Password Reset Verification Code'
    message = f'Your password reset code is: {code}\nThis code will expire in 30 seconds.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
from groq import Groq

key = "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"


def llm(questions_list, convoid, user_response, post_title, company_questions):
    """
    Modified interview function to work with Django models.

    Args:
        questions_list (list): List of previous questions from Customquestions model
        convoid (str): Conversation ID from Customconversation model
        user_response (str): Current user's response
        post_title (str): Job position from Custominterviews model
        company_questions (str): Questions text from Custominterviews model
    """
    # Format previous questions for context
    previous_questions = "\n".join([
        f"Q: {q}" for q in questions_list if q.strip()
    ]) if questions_list else "No prior questions."

    prompt = f"""
    You are conducting a formal professional interview as a Senior HR Representative for a position in {post_title}. You must strictly follow the company's requirements and questions.

    COMPANY REQUIREMENTS AND QUESTIONS:
    {company_questions}

    INTERVIEW CONTEXT:
    Position: {post_title}
    Conversation ID: {convoid}

    Previous Discussion:
    {previous_questions}

    Current Response:
    {user_response}

    REQUIRED OUTPUT FORMAT:
    Reply: [Provide a professional acknowledgment that:
    - Shows understanding of the candidate's response
    - Maintains professional tone
    - Stays focused on the current topic from company requirements]

    Next Question: [Either:
    1. Ask the next logical question from the company requirements that hasn't been covered yet
    2. If current response needs clarification, ask a follow-up strictly related to current topic
    3. If all topics from company requirements have been covered:
       - Write "INTERVIEW_COMPLETE" followed by a professional thank you message]

    IMPORTANT RULES:
    - Only ask questions specifically from the company requirements text
    - Track which topics have been covered through the previous questions
    - Once all required topics are covered, end with "INTERVIEW_COMPLETE"
    - If candidate asks questions after completion, respond courteously but do not ask new questions
    """

    try:
        client = Groq(api_key=key)

        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            temperature=0.6,
            top_p=0.9,
        )

        response_text = completion.choices[0].message.content
        print("Debug - Interview Response:", response_text)

        return parse_ai_response(response_text)

    except Exception as e:
        print(f"Interview System Error: {e}")
        return (
            "Thank you for your response. Let me review that according to our requirements.",
            "Could you please elaborate on your previous point?"
        )


def parse_ai_response(response_text):
    """
    Parse the AI response to extract reply and next question.
    Returns tuple of (reply, next_question)
    """
    try:
        lines = response_text.strip().split('\n')
        reply = ""
        next_question = ""
        current_section = None

        for line in lines:
            if line.startswith("Reply:"):
                current_section = "reply"
                reply = line.split("Reply:")[1].strip()
            elif line.startswith("Next Question:"):
                current_section = "question"
                next_question = line.split("Next Question:")[1].strip()
            elif line.strip() and current_section:
                if current_section == "reply":
                    reply += " " + line.strip()
                elif current_section == "question":
                    next_question += " " + line.strip()

        return reply.strip(), next_question.strip()

    except Exception as e:
        print(f"Error parsing AI response: {e}")
        return (
            "Thank you for your response.",
            "Let's continue with our discussion."
        )