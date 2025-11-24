import openai
import os
from dotenv import load_dotenv

load_dotenv()

def claude_triage(symptoms, medicines_df):
    """
    Use OpenAI GPT-4 for triage, fallback to keywords.
    """
    
    api_key = os.getenv('OPENAI_API_KEY', '')
    
    if not api_key:
        print("No OPENAI_API_KEY found in environment")
        return simple_keyword_triage(symptoms, medicines_df)
    
    print(f"Using OpenAI API key: {api_key[:15]}...{api_key[-4:]}")
    
    try:
        client = openai.OpenAI(api_key=api_key)
        
        medicine_list = "\n".join([
            f"- {row['Medicine_Name']}: For {row['Condition']}. Keywords: {row['Keywords']}"
            for _, row in medicines_df.iterrows()
        ])
        
        prompt = f"""You are an emergency medical triage assistant.

Available emergency medicines:
{medicine_list}

User's symptoms: "{symptoms}"

Respond with ONLY the exact medicine name from the list above (e.g., "Salbutamol Inhaler").
If symptoms don't clearly match, respond with "NONE".

Medicine name:"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a medical triage assistant. Respond only with medicine names."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0
        )
        
        response_text = response.choices[0].message.content.strip()
        print(f"OpenAI response: {response_text}")
        
        for _, med in medicines_df.iterrows():
            if med['Medicine_Name'].lower() in response_text.lower():
                return med
        
        for _, med in medicines_df.iterrows():
            med_name_parts = med['Medicine_Name'].lower().split()
            if any(part in response_text.lower() for part in med_name_parts if len(part) > 3):
                return med
        
        print(f"No medicine matched for response: {response_text}")
        return None
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return simple_keyword_triage(symptoms, medicines_df)

def simple_keyword_triage(symptoms, medicines_df):
    """
    Fallback keyword-based matching.
    """
    symptoms_lower = symptoms.lower()
    
    best_match = None
    best_score = 0
    
    for _, med in medicines_df.iterrows():
        keywords = med['Keywords'].lower().split(',')
        matches = sum(1 for keyword in keywords if keyword.strip() in symptoms_lower)
        if matches > best_score:
            best_score = matches
            best_match = med
    
    if best_score >= 2:
        return best_match
    
    return None
