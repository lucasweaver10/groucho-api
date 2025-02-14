from app.schemas import BlogPostRequest, BlogPostResponse
from app.services import content_brief_service, content_outline_service, content_section_service

def create_brief(request: BlogPostRequest):
    return content_brief_service.create_content_brief(request.brief_data)

def generate_outline(topic: str, content_brief):
    return content_outline_service.generate_outline(topic, content_brief)

def generate_sections(outline, content_brief):
    sections = []
    for idx, outline_section in enumerate(outline.sections):
        previous_section = sections[idx - 1] if idx > 0 else None
        next_outline_section = (
            outline.sections[idx + 1] if idx < len(outline.sections) - 1 else None
        )
        section = content_section_service.generate_content_section(
            content_brief=content_brief,
            current_outline_section=outline_section,
            previous_section=previous_section,
            next_outline_section=next_outline_section
        )
        sections.append(section)
    return sections

def assemble_full_content(sections):
    return "\n\n".join(sections)

def generate_blog_post(request: BlogPostRequest) -> BlogPostResponse:
    brief = create_brief(request)
    outline = generate_outline(request.topic, brief)
    sections = generate_sections(outline, brief)
    full_content = assemble_full_content(sections)
    
    return BlogPostResponse(
        content_brief=brief,
        outline=outline,
        sections=sections,
        full_content=full_content
    )
