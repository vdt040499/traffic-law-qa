"""Vietnamese text processing utilities."""

import re
from typing import List, Optional, Set
from underthesea import word_tokenize, pos_tag, sent_tokenize


class VietnameseProcessor:
    """Vietnamese text processing for traffic law documents."""
    
    def __init__(self):
        """Initialize Vietnamese text processor."""
        self.stop_words = self._load_stop_words()
        self.traffic_keywords = self._load_traffic_keywords()
    
    def _load_stop_words(self) -> Set[str]:
        """Load Vietnamese stop words."""
        return {
            "là", "của", "trong", "với", "về", "tại", "từ", "đến", "trên", "dưới",
            "và", "hoặc", "nhưng", "nếu", "khi", "để", "cho", "theo", "như",
            "có", "được", "bị", "sẽ", "đã", "đang", "chưa", "không", "phải",
            "này", "đó", "ấy", "kia", "những", "các", "mọi", "tất cả"
        }
    
    def _load_traffic_keywords(self) -> Set[str]:
        """Load traffic-related keywords."""
        return {
            "xe máy", "ô tô", "xe đạp", "phương tiện", "giao thông",
            "tốc độ", "vượt đèn đỏ", "đỗ xe", "bằng lái", "giấy tờ",
            "rượu bia", "nồng độ cồn", "mũ bảo hiểm", "đường phố",
            "làn đường", "vỉa hè", "đèn tín hiệu", "biển báo",
            "vi phạm", "phạt tiền", "tạm giữ", "thu hồi bằng lái"
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize Vietnamese text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters but keep Vietnamese diacritics
        text = re.sub(r'[^\w\s\u00C0-\u024F\u1E00-\u1EFF]', ' ', text)
        
        # Convert to lowercase
        text = text.lower()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize Vietnamese text into words."""
        try:
            return word_tokenize(text)
        except Exception:
            # Fallback to simple splitting if underthesea fails
            return text.split()
    
    def remove_stop_words(self, tokens: List[str]) -> List[str]:
        """Remove stop words from token list."""
        return [token for token in tokens if token.lower() not in self.stop_words]
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        cleaned_text = self.clean_text(text)
        tokens = self.tokenize(cleaned_text)
        
        # Remove stop words
        keywords = self.remove_stop_words(tokens)
        
        # Filter by minimum length
        keywords = [kw for kw in keywords if len(kw) >= 2]
        
        # Add traffic-specific keywords if found
        traffic_kws = []
        for kw in self.traffic_keywords:
            if kw in cleaned_text:
                traffic_kws.append(kw)
        
        return list(set(keywords + traffic_kws))
    
    def preprocess_for_embedding(self, text: str) -> str:
        """Preprocess text for embedding generation."""
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        filtered = self.remove_stop_words(tokens)
        return ' '.join(filtered)
    
    def sentence_split(self, text: str) -> List[str]:
        """Split text into sentences."""
        try:
            return sent_tokenize(text)
        except Exception:
            # Fallback to simple splitting
            return re.split(r'[.!?]+', text)


# Global processor instance
vietnamese_processor = VietnameseProcessor()


def get_vietnamese_processor() -> VietnameseProcessor:
    """Get Vietnamese text processor instance."""
    return vietnamese_processor