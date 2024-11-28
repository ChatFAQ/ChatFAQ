def convert_mml_to_llm_format(mml):
    """
    Converts the MML (Message Markup Language) format to the common LLM message format.

    :param mml: List of messages in MML format
    :return: List of messages in LLM format {'role': 'user', 'content': '...'}
    """
    roles_map = {
        "bot": "assistant",
        "human": "user",
    }
    messages = []

    for message in mml:
        for stack in message.get("stack", []):
            content = stack["payload"].get("content")
            if not content:
                continue
            messages.append({
                "role": roles_map[message["sender"]["type"]],
                "content": content,
            })

    return messages
