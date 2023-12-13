import guidance

def generate_query(passage: str, n_queries: int = 5):
    """
    
    """

    llm = guidance.llms.OpenAI('gpt-3.5-turbo-instruct')

    prompt = '''Generate questions for the following passage:
{{{{passage}}}}

\t- {{{{#geneach "queries" num_iterations={} join='\n\t-'}}}}{{{{gen 'this' temperature=0.2 stop=['-', '\n', '1.']}}}}{{{{/geneach}}}}
'''.format(n_queries)
    
    gen_query = guidance(
        prompt
    )

    result = gen_query(passage=passage, llm=llm)

    return [query.strip() for query in result['queries'] if query != '']

