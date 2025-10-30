from app.core.config import settings

def fetch_realtime_data(query: str):
    """
    Wrapper function to use Tavily client from config
    """
    tavily = settings.tavily_client
    return tavily.search(query)
