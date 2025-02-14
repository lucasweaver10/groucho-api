
from app.services.blog_post_orchestrator import generate_blog_post

# A registry mapping content types to functions
CONTENT_ORCHESTRATORS = {
    "blog_post": generate_blog_post,    
}

def orchestrate_content_generation(request):
    try:
        orchestrator = CONTENT_ORCHESTRATORS[request.content_type]
    except KeyError:
        raise ValueError(f"Unsupported content type: {request.content_type}")
    return orchestrator(request)