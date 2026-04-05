MEMORY_EXTRACTION_PROMPT = """Extract and format factual personal information about the user from their message.

OBJECTIVE:
Extract concrete, verifiable facts about the user. Ignore meta-commentary, requests to remember, 
conversational fillers, and instructions about memory itself.

CATEGORIES OF IMPORTANT FACTS:
- Personal: name, age, location, nationality, languages spoken
- Professional: job title, company, industry, education, skills, certifications
- Preferences: hobbies, favorites (food/music/books/movies), interests, dislikes
- Life context: family status, relationships, living situation, health conditions
- Experiences: significant achievements, past roles, travel, life events
- Goals: aspirations, plans, things they're working toward
- Habits: routines, regular activities, lifestyle patterns

EXTRACTION RULES:
1. Extract ONLY factual statements about the user
2. Ignore:
   - Requests to remember ("please remember", "make a note", "don't forget")
   - Questions or hypotheticals ("what if I told you", "should I mention")
   - Meta-commentary about memory ("for next time", "keep this in mind")
   - Conversational phrases ("hey", "by the way", "just so you know")
   - Opinions about remembering itself
   
3. Convert to third-person, present tense when possible
4. Be concise but preserve key details
5. If multiple facts exist, combine them logically
6. Mark as not important if:
   - No actual facts present (pure questions/greetings/requests)
   - Only meta-instructions about memory
   - Purely hypothetical or conditional statements

FORMAT GUIDELINES:
- Use present tense for current facts: "Works as...", "Lives in...", "Enjoys..."
- Use past tense for completed events: "Studied at...", "Worked at...", "Graduated from..."
- Keep it factual and neutral
- Preserve important context (e.g., "Senior Engineer" not just "Engineer")

EXAMPLES:

Input: "Hey, could you remember that I love Star Wars?"
Output: {{
    "is_important": true,
    "formatted_memory": "Loves Star Wars"
}}

Input: "Please make a note that I work as a senior software engineer at Google"
Output: {{
    "is_important": true,
    "formatted_memory": "Works as a senior software engineer at Google"
}}

Input: "Remember this: I live in Madrid and speak fluent Spanish"
Output: {{
    "is_important": true,
    "formatted_memory": "Lives in Madrid, speaks fluent Spanish"
}}

Input: "Can you remember my details for next time?"
Output: {{
    "is_important": false,
    "formatted_memory": null
}}

Input: "Hey, how are you today?"
Output: {{
    "is_important": false,
    "formatted_memory": null
}}

Input: "I studied computer science at MIT and graduated in 2020"
Output: {{
    "is_important": true,
    "formatted_memory": "Studied computer science at MIT, graduated in 2020"
}}

Input: "Just FYI, I'm vegetarian and allergic to peanuts"
Output: {{
    "is_important": true,
    "formatted_memory": "Vegetarian, allergic to peanuts"
}}

Input: "BTW I'm currently learning Japanese and planning to visit Tokyo next year"
Output: {{
    "is_important": true,
    "formatted_memory": "Currently learning Japanese, planning to visit Tokyo next year"
}}

Input: "What if I told you I like pizza?"
Output: {{
    "is_important": true,
    "formatted_memory": "Likes pizza"
}}
Reason: Despite hypothetical phrasing, contains actual preference

Input: "I might be interested in learning guitar someday"
Output: {{
    "is_important": true,
    "formatted_memory": "Interested in learning guitar"
}}
Reason: Expresses genuine interest/goal despite uncertainty

Input: "Don't forget about our conversation"
Output: {{
    "is_important": false,
    "formatted_memory": null
}}
Reason: Pure meta-instruction, no facts

Input: "I used to work at Amazon but now I'm at Microsoft as a PM, and I have a degree in business from Stanford"
Output: {{
    "is_important": true,
    "formatted_memory": "Previously worked at Amazon, currently works at Microsoft as a Product Manager, has a business degree from Stanford"
}}
Reason: Multiple facts combined with temporal context

Now extract from this message:
Message: {message}

Output (JSON only, no explanation):
"""