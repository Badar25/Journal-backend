from typing import List, Dict, Optional
from ..models.response import APIResponse
from ..core.logger import logger

class JournalTextExtractor:
    @staticmethod
    def extract_journal_texts(journals: List[Dict]) -> List[str]:
        """Extract formatted text from journal entries handling missing fields."""
        journal_texts = []
        for journal in journals:
            title = journal.get("title", "").strip()
            content = journal.get("content", "").strip()
            
            if title and content:
                journal_texts.append(f"{title}: {content}")
            elif title:
                journal_texts.append(title)
            elif content:
                journal_texts.append(content)
        return journal_texts

    @staticmethod
    def process_journals_response(response: APIResponse, context_type: str = "journals") -> tuple[Optional[str], Optional[APIResponse]]:
        """Process journal response and return context string or error response."""
        if not response.success:
            return None, response
        
        journals = response.data.get("journals", [])
        if not journals:
            return None, APIResponse.success_response(
                data={"response": f"No {context_type} found."},
                message=f"No {context_type} found"
            )
        
        journal_texts = JournalTextExtractor.extract_journal_texts(journals)
        if not journal_texts:
            return None, APIResponse.success_response(
                data={"response": f"No valid content found in {context_type}."},
                message="No valid content found"
            )
        
        return "\n".join(journal_texts), None