class PromptTemplates:
    @staticmethod
    def get_chat_prompt(context: str, query: str) -> str:
        return (
            f"You're chatting with me based on my journal entries from the last few days: '{context}'. "
            f"Respond to my message '{query}' as if you're my journals talking back to me in a casual, friendly way. "
            "Keep it natural and stick to what's in the context."
        )

    @staticmethod
    def get_summary_prompt(days: int, context: str) -> str:
        return (
            f"Summarize my journal entries from the last {days} days based only on the provided context. "
            "Do not provide guidance, disclaimers, or mention missing information. "
            "Focus strictly on key themes, emotions, and recurring topics in a 4-5 line narrative summary. "
            "Address me directly as 'you' since these are my journals, avoiding third-person references. "
            f"Context: '{context}'"
        )

prompt_templates = PromptTemplates()