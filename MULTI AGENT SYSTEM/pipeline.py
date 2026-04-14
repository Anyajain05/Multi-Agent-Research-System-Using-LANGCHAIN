import re
from agents import writer_chain, critic_chain
from tools import scrape_url_raw, search_web_raw, format_search_results


def extract_urls(text: str) -> list[str]:
    urls = re.findall(r"https?://[^\s)\]>\"']+", text)
    # Preserve order and remove duplicates.
    return list(dict.fromkeys(urls))

def run_research_pipeline(topic : str) -> dict:

    state = {}

    #search agent working 
    print("\n"+" ="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    search_results = search_web_raw(query=topic, max_results=5)
    state["search_results"] = format_search_results(search_results)

    print("\n search result ",state['search_results'])

    #step 2 - reader agent 
    print("\n"+" ="*50)
    print("step 2 - Reader agent is scraping top resources ...")
    print("="*50)

    urls = extract_urls(state["search_results"])
    scraped_chunks = []
    for url in urls[:3]:
        content = scrape_url_raw(url=url, timeout=8)
        if not content.startswith("Could not scrape URL:"):
            scraped_chunks.append(f"Source: {url}\n{content}")

    if scraped_chunks:
        state["scraped_content"] = "\n\n".join(scraped_chunks)
    else:
        state["scraped_content"] = "No source could be scraped successfully from the discovered URLs."

    print("\nscraped content: \n", state['scraped_content'])

    #step 3 - writer chain 

    print("\n"+" ="*50)
    print("step 3 - Writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n Final Report\n",state['report'])

    #critic report 

    print("\n"+" ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report":state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state



if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)