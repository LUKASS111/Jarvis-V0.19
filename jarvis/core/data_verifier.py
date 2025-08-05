"""
Data Verification System for Jarvis-V0.19
Implements dual-model verification with confidence scoring.
"""

import asyncio
import json
import threading
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
import sqlite3

from ..llm.llm_interface import ask_local_llm, get_available_models, CURRENT_OLLAMA_MODEL
from .data_archiver import get_archiver, ArchiveEntry

@dataclass
class VerificationResult:
    """Result of data verification"""
    is_verified: bool
    confidence_score: float  # 0.0 to 1.0
    verification_model: str
    reasoning: str
    timestamp: str
    verification_type: str  # fact_check, logical_consistency, format_validation, etc.
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_verified': self.is_verified,
            'confidence_score': self.confidence_score,
            'verification_model': self.verification_model,
            'reasoning': self.reasoning,
            'timestamp': self.timestamp,
            'verification_type': self.verification_type
        }

class DataVerifier:
    """Main data verification system using dual-model approach"""
    
    def __init__(self):
        self.archiver = get_archiver()
        self.verification_models = self._get_verification_models()
        self.verification_lock = threading.Lock()
        self.verification_active = True
        
        # Start background verification worker
        self.worker_thread = threading.Thread(target=self._verification_worker, daemon=True)
        self.worker_thread.start()
    
    def _get_verification_models(self) -> List[str]:
        """Get list of models suitable for verification"""
        available = get_available_models()
        # Prefer different models for verification to avoid bias
        primary_model = CURRENT_OLLAMA_MODEL
        verification_models = [m for m in available if m != primary_model]
        if not verification_models:
            verification_models = available  # fallback to any available model
        return verification_models
    
    def _verification_worker(self):
        """Background worker for continuous verification"""
        while self.verification_active:
            try:
                pending_entries = self.archiver.get_pending_verification(limit=5)
                if not pending_entries:
                    time.sleep(2)  # Wait before checking again
                    continue
                
                for entry in pending_entries:
                    if not self.verification_active:
                        break
                    
                    try:
                        result = self._verify_entry(entry)
                        status = 'verified' if result.is_verified else 'rejected'
                        
                        self.archiver.update_verification(
                            entry.id,
                            status,
                            result.confidence_score,
                            result.verification_model,
                            json.dumps(result.to_dict())
                        )
                        
                        # Log verification activity
                        self.archiver.log_agent_activity(
                            'verification_system',
                            'data_verification',
                            f'Verified entry {entry.id}: {status}',
                            result.to_dict()
                        )
                        
                    except Exception as e:
                        self.archiver.update_verification(
                            entry.id,
                            'error',
                            0.0,
                            'verification_system',
                            f'Verification error: {str(e)}'
                        )
                        print(f"[WARN] Verification error for entry {entry.id}: {e}")
                
            except Exception as e:
                print(f"[ERROR] Verification worker error: {e}")
                time.sleep(5)  # Wait longer on error
    
    def _verify_entry(self, entry: ArchiveEntry) -> VerificationResult:
        """Verify a single archive entry"""
        verification_type = self._determine_verification_type(entry)
        verification_model = self.verification_models[0] if self.verification_models else CURRENT_OLLAMA_MODEL
        
        if verification_type == 'fact_check':
            return self._verify_factual_content(entry, verification_model)
        elif verification_type == 'logical_consistency':
            return self._verify_logical_consistency(entry, verification_model)
        elif verification_type == 'format_validation':
            return self._verify_format(entry, verification_model)
        elif verification_type == 'code_validation':
            return self._verify_code(entry, verification_model)
        else:
            return self._verify_general_content(entry, verification_model)
    
    def _determine_verification_type(self, entry: ArchiveEntry) -> str:
        """Determine what type of verification is needed"""
        content = entry.content.lower()
        
        if entry.data_type == 'input' and any(keyword in content for keyword in ['fact', 'information', 'data', 'statistics']):
            return 'fact_check'
        elif 'code' in entry.source.lower() or any(lang in content for lang in ['python', 'javascript', 'def ', 'function', 'class ']):
            return 'code_validation'
        elif entry.data_type == 'output' and 'logic' in entry.operation.lower():
            return 'logical_consistency'
        elif 'format' in entry.operation.lower() or 'json' in content or 'xml' in content:
            return 'format_validation'
        else:
            return 'general_content'
    
    def _verify_factual_content(self, entry: ArchiveEntry, model: str) -> VerificationResult:
        """Verify factual information using LLM"""
        verification_prompt = f"""
You are a fact-checking system. Analyze the following information and determine if it's factually accurate.

Content to verify: {entry.content}
Source: {entry.source}
Operation: {entry.operation}

Please respond in the following JSON format:
{{
    "is_accurate": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "explanation of your assessment",
    "concerns": ["list of any concerns or uncertainties"]
}}

Be conservative - if you're unsure, mark as false with low confidence.
"""
        
        try:
            response = ask_local_llm(verification_prompt, model=model, timeout=30)
            result_data = self._parse_verification_response(response)
            
            return VerificationResult(
                is_verified=result_data.get('is_accurate', False),
                confidence_score=result_data.get('confidence', 0.0),
                verification_model=model,
                reasoning=result_data.get('reasoning', 'No reasoning provided'),
                timestamp=datetime.now().isoformat(),
                verification_type='fact_check'
            )
            
        except Exception as e:
            return VerificationResult(
                is_verified=False,
                confidence_score=0.0,
                verification_model=model,
                reasoning=f'Verification failed: {str(e)}',
                timestamp=datetime.now().isoformat(),
                verification_type='fact_check'
            )
    
    def _verify_logical_consistency(self, entry: ArchiveEntry, model: str) -> VerificationResult:
        """Verify logical consistency of content"""
        verification_prompt = f"""
You are a logical consistency checker. Analyze the following content for logical consistency and coherence.

Content: {entry.content}
Context: Generated from {entry.source} during {entry.operation}

Check for:
1. Internal contradictions
2. Logical flow
3. Coherence with context
4. Reasonableness of conclusions

Respond in JSON format:
{{
    "is_consistent": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "explanation",
    "logical_issues": ["list of any logical problems found"]
}}
"""
        
        try:
            response = ask_local_llm(verification_prompt, model=model, timeout=30)
            result_data = self._parse_verification_response(response)
            
            return VerificationResult(
                is_verified=result_data.get('is_consistent', False),
                confidence_score=result_data.get('confidence', 0.0),
                verification_model=model,
                reasoning=result_data.get('reasoning', 'No reasoning provided'),
                timestamp=datetime.now().isoformat(),
                verification_type='logical_consistency'
            )
            
        except Exception as e:
            return VerificationResult(
                is_verified=False,
                confidence_score=0.0,
                verification_model=model,
                reasoning=f'Verification failed: {str(e)}',
                timestamp=datetime.now().isoformat(),
                verification_type='logical_consistency'
            )
    
    def _verify_format(self, entry: ArchiveEntry, model: str) -> VerificationResult:
        """Verify format correctness (JSON, XML, etc.)"""
        content = entry.content.strip()
        
        # Try to validate common formats
        format_valid = False
        reasoning = ""
        confidence = 0.0
        
        if content.startswith('{') and content.endswith('}'):
            try:
                json.loads(content)
                format_valid = True
                reasoning = "Valid JSON format"
                confidence = 0.95
            except json.JSONDecodeError as e:
                reasoning = f"Invalid JSON: {str(e)}"
                confidence = 0.1
        
        elif content.startswith('<') and content.endswith('>'):
            # Basic XML validation
            if content.count('<') == content.count('>'):
                format_valid = True
                reasoning = "Basic XML structure appears valid"
                confidence = 0.8
            else:
                reasoning = "Mismatched XML tags"
                confidence = 0.1
        
        else:
            # Use LLM for other format validation
            try:
                verification_prompt = f"""
Analyze this content for format correctness:

Content: {content}
Expected context: {entry.operation}

Is this content properly formatted for its intended purpose?
Respond in JSON: {{"is_valid": true/false, "confidence": 0.0-1.0, "reasoning": "explanation"}}
"""
                response = ask_local_llm(verification_prompt, model=model, timeout=20)
                result_data = self._parse_verification_response(response)
                format_valid = result_data.get('is_valid', False)
                confidence = result_data.get('confidence', 0.0)
                reasoning = result_data.get('reasoning', 'No reasoning provided')
                
            except Exception as e:
                reasoning = f"Format verification failed: {str(e)}"
                confidence = 0.0
        
        return VerificationResult(
            is_verified=format_valid,
            confidence_score=confidence,
            verification_model=model,
            reasoning=reasoning,
            timestamp=datetime.now().isoformat(),
            verification_type='format_validation'
        )
    
    def _verify_code(self, entry: ArchiveEntry, model: str) -> VerificationResult:
        """Verify code correctness and safety"""
        verification_prompt = f"""
You are a code safety and correctness checker. Analyze this code:

Code: {entry.content}
Context: {entry.operation}

Check for:
1. Syntax correctness
2. Potential security issues
3. Logic errors
4. Best practices

Respond in JSON:
{{
    "is_safe_and_correct": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "explanation",
    "issues": ["list of any issues found"],
    "suggestions": ["improvement suggestions"]
}}
"""
        
        try:
            response = ask_local_llm(verification_prompt, model=model, timeout=45)
            result_data = self._parse_verification_response(response)
            
            return VerificationResult(
                is_verified=result_data.get('is_safe_and_correct', False),
                confidence_score=result_data.get('confidence', 0.0),
                verification_model=model,
                reasoning=result_data.get('reasoning', 'No reasoning provided'),
                timestamp=datetime.now().isoformat(),
                verification_type='code_validation'
            )
            
        except Exception as e:
            return VerificationResult(
                is_verified=False,
                confidence_score=0.0,
                verification_model=model,
                reasoning=f'Code verification failed: {str(e)}',
                timestamp=datetime.now().isoformat(),
                verification_type='code_validation'
            )
    
    def _verify_general_content(self, entry: ArchiveEntry, model: str) -> VerificationResult:
        """General content verification"""
        verification_prompt = f"""
Analyze this content for overall quality and appropriateness:

Content: {entry.content}
Source: {entry.source}
Operation: {entry.operation}

Evaluate:
1. Content quality
2. Appropriateness for the context
3. Completeness
4. Coherence

Respond in JSON:
{{
    "is_acceptable": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "explanation",
    "quality_score": 0.0-1.0
}}
"""
        
        try:
            response = ask_local_llm(verification_prompt, model=model, timeout=30)
            result_data = self._parse_verification_response(response)
            
            return VerificationResult(
                is_verified=result_data.get('is_acceptable', False),
                confidence_score=result_data.get('confidence', 0.0),
                verification_model=model,
                reasoning=result_data.get('reasoning', 'No reasoning provided'),
                timestamp=datetime.now().isoformat(),
                verification_type='general_content'
            )
            
        except Exception as e:
            return VerificationResult(
                is_verified=False,
                confidence_score=0.0,
                verification_model=model,
                reasoning=f'General verification failed: {str(e)}',
                timestamp=datetime.now().isoformat(),
                verification_type='general_content'
            )
    
    def _parse_verification_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM verification response"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback parsing
                return self._fallback_parse(response)
        except Exception:
            return self._fallback_parse(response)
    
    def _fallback_parse(self, response: str) -> Dict[str, Any]:
        """Fallback parsing when JSON extraction fails"""
        response_lower = response.lower()
        
        # Determine verification result
        is_verified = any(word in response_lower for word in ['true', 'yes', 'correct', 'valid', 'accurate'])
        
        # Estimate confidence based on certainty indicators
        confidence = 0.5  # default
        if any(word in response_lower for word in ['certain', 'confident', 'sure', 'definitely']):
            confidence = 0.8
        elif any(word in response_lower for word in ['uncertain', 'maybe', 'possibly', 'unclear']):
            confidence = 0.3
        
        return {
            'is_verified': is_verified,
            'confidence': confidence,
            'reasoning': response[:200] + '...' if len(response) > 200 else response
        }
    
    def stop_verification(self):
        """Stop the verification worker"""
        self.verification_active = False
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=5)
    
    def force_verify_entry(self, entry_id: int) -> VerificationResult:
        """Force immediate verification of a specific entry"""
        archiver = get_archiver()
        with archiver._archive_lock:
            conn = sqlite3.connect(archiver.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM archive_entries WHERE id = ?', (entry_id,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                raise ValueError(f"Entry {entry_id} not found")
            
            metadata = json.loads(row[7]) if row[7] else {}
            entry = ArchiveEntry(
                id=row[0], timestamp=row[1], data_type=row[2],
                content=row[3], source=row[4], operation=row[5],
                content_hash=row[6], metadata=metadata,
                verification_status=row[8], verification_score=row[9],
                verification_model=row[10], verification_timestamp=row[11],
                verification_details=row[12]
            )
            
            result = self._verify_entry(entry)
            status = 'verified' if result.is_verified else 'rejected'
            
            archiver.update_verification(
                entry.id,
                status,
                result.confidence_score,
                result.verification_model,
                json.dumps(result.to_dict())
            )
            
            return result

# Global verifier instance
_verifier = None

def get_verifier() -> DataVerifier:
    """Get global verifier instance (singleton pattern)"""
    global _verifier
    if _verifier is None:
        _verifier = DataVerifier()
    return _verifier

def verify_data_immediately(content: str, data_type: str, source: str, operation: str) -> VerificationResult:
    """Immediately verify data without archiving"""
    entry = ArchiveEntry(
        id=None,
        timestamp=datetime.now().isoformat(),
        data_type=data_type,
        content=content,
        source=source,
        operation=operation,
        content_hash="immediate_verification",
        metadata={},
        verification_status='pending',
        verification_score=None,
        verification_model=None,
        verification_timestamp=None,
        verification_details=None
    )
    
    verifier = get_verifier()
    return verifier._verify_entry(entry)

def is_data_safe_to_use(archive_entry_id: int, min_confidence: float = 0.7) -> bool:
    """Check if archived data is safe to use based on verification"""
    archiver = get_archiver()
    with archiver._archive_lock:
        conn = sqlite3.connect(archiver.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT verification_status, verification_score 
            FROM archive_entries WHERE id = ?
        ''', (archive_entry_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return False
        
        status, score = row
        return status == 'verified' and (score or 0.0) >= min_confidence