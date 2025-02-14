# Steps
User wants to generate a blog post
User chooses a topic for the blog post
User fills out a form to create a content brief
Groucho generates a blog post outline based on the content brief and the chosen topic
Groucho generates a blog post section by section based on the outline and the content brief
Each "content section" is generated from its corresponding outline section, and the next outline section, and the previous content section, along with fields from the content brief
Content sections are concatenated together to make "content.text", or we can use all related content_sections on their correct order to make the final content


Considerations:
How to track state/changes in content, i.e. Git for docs/text?
How about a "revision history" for each content section?
How about adding an AI-generated summary for each content section that can be used for RAG-type purposes by the LLM later?
How about adding in a model for corrected_content_sections that allows users to write their own updated version of the content we can use to train a custom model on later?
Let's add a field to the "content_section" model that allows us to give a "weight/score" to the section from 0-10 for how good we thought that section was related to what we expect (to be used for training later)
Make it multi-tenant by adding an organization_id field to all content models owned by an id?