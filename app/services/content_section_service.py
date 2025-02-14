from fastapi import HTTPException
from sqlmodel import Session
from ..dependencies import get_db
import logging
from pydantic import BaseModel
from app.agents.content_writer_agent import content_writer_agent, Deps

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

system_prompt = '''
'You are an expert blog post writer, capable of creating engaging and informative content. You specialize in SEO using semantic networks in your writing to rank highly on Google.'
        'Use markdown formatting and write a section for a blog post based on the given outline section in the same language. Use a combination of paragraphs, lists, and tables for a better reader experience.'
        'Don\'t use any click-baity language.'
        'Must never use the words "introduction" or "conclusion" in the text.'
        'Use a \'front-loading\' or \'keyword-prioritized\' writing style, placing the primary keywords in beginning parts of the sentences, and the secondary keywords in the predicates.'
        'You be given the outline for the next section, so you can make sure not to write about anything that will be covered there.'
        'You be given a writing sample that you should mock the style of as closely as possible.'
        'You will be given a product description of the product we\'re trying to promote and rank for with this blog post. Adapt your content to meet those needs as appropriate.'
        'You will be given a list of negative words that we don\'t want to use in this blog post. Avoid these words.'
        'Generate the content without including the outline text. Start with an appropriate ## h2 heading.'
        'Don\'t write a conclusion for the section, just seamlessly transition into the next section with one sentence in a natural way if necessary.'        
        '''

user_prompt = '''
Outline section:
[section]
    - IELTS Writing Tips for Success
    - Provide effective tips for approaching both tasks in the writing test.
    - Discuss the importance of understanding the task requirements and questions.
    - Emphasize the value of practice and feedback in improving writing skills.

Writing Sample:
What's the benefit for you? Objective Feedback The AI provides unbiased, consistent feedback on your pronunciation, helping you identify areas for improvement. Previously this was something only available if you paid for private lessons with a language tutor. But now, you can have your very own personalized AI speaking coach help you learn how to improve and correct your pronunciation in your target language. Improved Pronunciation By receiving detailed scores (extra details are only available in certain languages), you can pinpoint specific pronunciation issues and work on them, resulting in you having clearer and more accurate speech. Boosted Confidence Knowing that you're pronouncing words correctly can significantly boost your confidence when speaking a new language. While the AI scores may not always be perfect (although sometimes they're scary close!), they're certainly good enough to tell you if you're on the right track with pronouncing even the trickiest of words.

Next section's outline:
[section]
    - Understanding IELTS Writing Task 1
    - Outline the structure and requirements of Task 1.
    - Discuss common types of questions and how to approach them.
    - Highlight the importance of data interpretation and summarization skills.

Product description:
IELTS Writing Checker: Get your IELTS Writing Essays checked by AI or an expert IELTS teacher to get feedback on how you can improve to get the IELTS Writing score you need THE FIRST TIME. Featuring custom trained models and a free and premium version.

Negative words:
n/a
'''

async def generate_content_section():
    try:
        deps = Deps(system_prompt=system_prompt)
        response = await content_writer_agent.run(user_prompt, deps=deps)
        return {"content_block": response.data}
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))