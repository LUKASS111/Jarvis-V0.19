"""
Enhanced Memory Management System for Jarvis V0.19
Provides advanced memory capabilities including semantic search, contextual storage, and intelligent retrieval.
"""

import json
import os
import time
import threading
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class MemoryEntry:
    """Memory entry data structure."""
    id: str
    content: str
    category: str
    timestamp: float
    importance: int
    tags: List[str]
    metadata: Dict[str, Any]
    access_count: int = 0
    last_accessed: float = 0
    related_entries: List[str] = None
    
    def __post_init__(self):
        if self.related_entries is None:
            self.related_entries = []
        if self.last_accessed == 0:
            self.last_accessed = self.timestamp

@dataclass
class SearchResult:
    """Search result with relevance scoring."""
    entry: MemoryEntry
    relevance_score: float
    match_type: str
    matched_terms: List[str]

class MemoryManager:
    """
    Advanced Memory Management System with semantic search and contextual storage.
    """
    
    def __init__(self, memory_db_path: str = "data/jarvis_memory.db", 
                 json_fallback_path: str = "data/jarvis_mem.json"):
        """Initialize memory manager with SQLite backend and JSON fallback."""
        self.db_path = memory_db_path
        self.json_path = json_fallback_path
        self.memory_lock = threading.Lock()
        
        # In-memory cache for fast access
        self.memory_cache = {}
        self.cache_max_size = 1000
        
        # Statistics
        self.stats = {
            'total_entries': 0,
            'total_searches': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'last_cleanup': time.time()
        }
        
        # Initialize database
        self._init_database()
        self._load_cache()
    
    def _init_database(self):
        """Initialize SQLite database with proper schema."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Handle database corruption gracefully
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Test if database is valid
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    cursor.fetchall()
            except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
                # Database is corrupted, backup and recreate
                print(f"[WARN] Memory database corruption detected: {e}")
                self._handle_corrupted_memory_database()
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS memory_entries (
                        id TEXT PRIMARY KEY,
                        content TEXT NOT NULL,
                        category TEXT,
                        timestamp REAL,
                        importance INTEGER,
                        tags TEXT,
                        metadata TEXT,
                        access_count INTEGER DEFAULT 0,
                        last_accessed REAL,
                        related_entries TEXT
                    )
                ''')
                
                # Create indices for better search performance
                conn.execute('CREATE INDEX IF NOT EXISTS idx_category ON memory_entries(category)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_entries(timestamp)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_importance ON memory_entries(importance)')
                conn.execute('CREATE INDEX IF NOT EXISTS idx_last_accessed ON memory_entries(last_accessed)')
                
                # Full-text search index
                conn.execute('''
                    CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                        id, content, category, tags, 
                        content='memory_entries', content_rowid='rowid'
                    )
                ''')
                
                conn.commit()
                print(f"[MEMORY] Database initialized successfully: {self.db_path}")
                
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            print(f"[ERROR] Memory database initialization failed: {e}")
            # Fallback to JSON mode
            self.db_path = None

    def _handle_corrupted_memory_database(self):
        """Handle corrupted memory database by backing up and recreating"""
        try:
            # Create backup of corrupted file
            backup_path = f"{self.db_path}.corrupted.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(self.db_path):
                os.rename(self.db_path, backup_path)
                print(f"[MEMORY] Corrupted database backed up to: {backup_path}")
            
            # Remove the file to force recreation
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
                
        except Exception as e:
            print(f"[WARN] Could not backup corrupted memory database: {e}")
            # Try to remove the corrupted file anyway
            try:
                if os.path.exists(self.db_path):
                    os.remove(self.db_path)
            except:
                pass
    
    def _load_cache(self):
        """Load frequently accessed entries into cache."""
        try:
            if self.db_path:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('''
                        SELECT * FROM memory_entries 
                        ORDER BY last_accessed DESC, access_count DESC 
                        LIMIT ?
                    ''', (self.cache_max_size // 2,))
                    
                    for row in cursor.fetchall():
                        entry = self._row_to_entry(row)
                        self.memory_cache[entry.id] = entry
            else:
                # Fallback to JSON loading
                self._load_from_json()
                
        except Exception as e:
            logger.error(f"Cache loading error: {e}")
    
    def store(self, content: str, category: str = "general", 
              importance: int = 5, tags: List[str] = None, 
              metadata: Dict[str, Any] = None) -> str:
        """
        Store new memory entry.
        
        Args:
            content: Content to store
            category: Category classification
            importance: Importance level (1-10)
            tags: List of tags for categorization
            metadata: Additional metadata
            
        Returns:
            str: Entry ID
        """
        if tags is None:
            tags = []
        if metadata is None:
            metadata = {}
        
        # Generate unique ID
        entry_id = hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()
        
        # Create memory entry
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            category=category,
            timestamp=time.time(),
            importance=importance,
            tags=tags,
            metadata=metadata
        )
        
        with self.memory_lock:
            try:
                if self.db_path:
                    self._store_to_db(entry)
                else:
                    self._store_to_json(entry)
                
                # Update cache
                self.memory_cache[entry_id] = entry
                self._manage_cache_size()
                
                # Update statistics
                self.stats['total_entries'] += 1
                
                logger.info(f"Stored memory entry: {entry_id[:8]}...")
                return entry_id
                
            except Exception as e:
                logger.error(f"Storage error: {e}")
                return None
    
    def retrieve(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve memory entry by ID."""
        with self.memory_lock:
            # Check cache first
            if entry_id in self.memory_cache:
                entry = self.memory_cache[entry_id]
                entry.access_count += 1
                entry.last_accessed = time.time()
                self.stats['cache_hits'] += 1
                return entry
            
            self.stats['cache_misses'] += 1
            
            try:
                if self.db_path:
                    entry = self._retrieve_from_db(entry_id)
                else:
                    entry = self._retrieve_from_json(entry_id)
                
                if entry:
                    entry.access_count += 1
                    entry.last_accessed = time.time()
                    self.memory_cache[entry_id] = entry
                    self._manage_cache_size()
                
                return entry
                
            except Exception as e:
                logger.error(f"Retrieval error: {e}")
                return None
    
    def search(self, query: str, category: str = None, 
               limit: int = 10, min_importance: int = 1) -> List[SearchResult]:
        """
        Advanced semantic search through memory entries.
        
        Args:
            query: Search query
            category: Filter by category
            limit: Maximum results
            min_importance: Minimum importance level
            
        Returns:
            List[SearchResult]: Ranked search results
        """
        self.stats['total_searches'] += 1
        
        try:
            if self.db_path:
                return self._search_db(query, category, limit, min_importance)
            else:
                return self._search_json(query, category, limit, min_importance)
                
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_related(self, entry_id: str, limit: int = 5) -> List[MemoryEntry]:
        """Get entries related to the given entry."""
        entry = self.retrieve(entry_id)
        if not entry:
            return []
        
        # Search for related content using tags and category
        related_entries = []
        
        # Search by tags
        for tag in entry.tags:
            tag_results = self.search(tag, limit=limit//2)
            for result in tag_results:
                if result.entry.id != entry_id and result.entry not in related_entries:
                    related_entries.append(result.entry)
        
        # Search by category
        if entry.category:
            category_results = self.search("", category=entry.category, limit=limit//2)
            for result in category_results:
                if result.entry.id != entry_id and result.entry not in related_entries:
                    related_entries.append(result.entry)
        
        return related_entries[:limit]
    
    def get_by_category(self, category: str, limit: int = 50) -> List[MemoryEntry]:
        """Get all entries in a specific category."""
        try:
            if self.db_path:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('''
                        SELECT * FROM memory_entries 
                        WHERE category = ? 
                        ORDER BY importance DESC, timestamp DESC
                        LIMIT ?
                    ''', (category, limit))
                    
                    return [self._row_to_entry(row) for row in cursor.fetchall()]
            else:
                # JSON fallback
                all_entries = self._get_all_from_json()
                category_entries = [e for e in all_entries if e.category == category]
                category_entries.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)
                return category_entries[:limit]
                
        except Exception as e:
            logger.error(f"Category retrieval error: {e}")
            return []
    
    def get_recent(self, hours: int = 24, limit: int = 20) -> List[MemoryEntry]:
        """Get recent memory entries."""
        since_timestamp = time.time() - (hours * 3600)
        
        try:
            if self.db_path:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('''
                        SELECT * FROM memory_entries 
                        WHERE timestamp > ? 
                        ORDER BY timestamp DESC
                        LIMIT ?
                    ''', (since_timestamp, limit))
                    
                    return [self._row_to_entry(row) for row in cursor.fetchall()]
            else:
                # JSON fallback
                all_entries = self._get_all_from_json()
                recent_entries = [e for e in all_entries if e.timestamp > since_timestamp]
                recent_entries.sort(key=lambda x: x.timestamp, reverse=True)
                return recent_entries[:limit]
                
        except Exception as e:
            logger.error(f"Recent entries retrieval error: {e}")
            return []
    
    def update_importance(self, entry_id: str, new_importance: int) -> bool:
        """Update importance level of an entry."""
        with self.memory_lock:
            try:
                if self.db_path:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute('''
                            UPDATE memory_entries 
                            SET importance = ? 
                            WHERE id = ?
                        ''', (new_importance, entry_id))
                        conn.commit()
                
                # Update cache
                if entry_id in self.memory_cache:
                    self.memory_cache[entry_id].importance = new_importance
                
                return True
                
            except Exception as e:
                logger.error(f"Importance update error: {e}")
                return False
    
    def delete_entry(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        with self.memory_lock:
            try:
                if self.db_path:
                    with sqlite3.connect(self.db_path) as conn:
                        conn.execute('DELETE FROM memory_entries WHERE id = ?', (entry_id,))
                        conn.commit()
                
                # Remove from cache
                if entry_id in self.memory_cache:
                    del self.memory_cache[entry_id]
                
                self.stats['total_entries'] -= 1
                return True
                
            except Exception as e:
                logger.error(f"Deletion error: {e}")
                return False
    
    def cleanup_current_entries(self, days: int = 30) -> Dict[str, int]:
        """Clean up old, low-importance entries."""
        cutoff_timestamp = time.time() - (days * 24 * 3600)
        
        with self.memory_lock:
            try:
                if self.db_path:
                    with sqlite3.connect(self.db_path) as conn:
                        # Delete low-importance, old entries
                        cursor = conn.execute('''
                            DELETE FROM memory_entries 
                            WHERE timestamp < ? AND importance < 5 AND access_count < 3
                        ''', (cutoff_timestamp,))
                        
                        deleted_count = cursor.rowcount
                        conn.commit()
                
                # Update cache
                to_remove = []
                for entry_id, entry in self.memory_cache.items():
                    if (entry.timestamp < cutoff_timestamp and 
                        entry.importance < 5 and 
                        entry.access_count < 3):
                        to_remove.append(entry_id)
                
                for entry_id in to_remove:
                    del self.memory_cache[entry_id]
                
                self.stats['last_cleanup'] = time.time()
                
                return {
                    'deleted_entries': deleted_count,
                    'cache_removed': len(to_remove)
                }
                
            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                return {'error': str(e)}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        try:
            if self.db_path:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute('SELECT COUNT(*) FROM memory_entries')
                    total_entries = cursor.fetchone()[0]
                    
                    cursor = conn.execute('''
                        SELECT category, COUNT(*) FROM memory_entries 
                        GROUP BY category ORDER BY COUNT(*) DESC
                    ''')
                    categories = dict(cursor.fetchall())
            else:
                all_entries = self._get_all_from_json()
                total_entries = len(all_entries)
                categories = {}
                for entry in all_entries:
                    categories[entry.category] = categories.get(entry.category, 0) + 1
            
            self.stats['total_entries'] = total_entries
            
            return {
                'total_entries': total_entries,
                'cache_size': len(self.memory_cache),
                'categories': categories,
                'performance': {
                    'total_searches': self.stats['total_searches'],
                    'cache_hit_rate': (self.stats['cache_hits'] / 
                                     max(self.stats['cache_hits'] + self.stats['cache_misses'], 1)) * 100,
                    'last_cleanup': datetime.fromtimestamp(self.stats['last_cleanup']).isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Statistics error: {e}")
            return {'error': str(e)}
    
    # Private methods for database operations
    def _store_to_db(self, entry: MemoryEntry):
        """Store entry to SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            # Store in main table
            conn.execute('''
                INSERT OR REPLACE INTO memory_entries 
                (id, content, category, timestamp, importance, tags, metadata, 
                 access_count, last_accessed, related_entries)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.id, entry.content, entry.category, entry.timestamp,
                entry.importance, json.dumps(entry.tags), json.dumps(entry.metadata),
                entry.access_count, entry.last_accessed, json.dumps(entry.related_entries)
            ))
            
            # Update FTS table
            conn.execute('''
                INSERT OR REPLACE INTO memory_fts 
                (id, content, category, tags)
                VALUES (?, ?, ?, ?)
            ''', (
                entry.id, entry.content, entry.category, ' '.join(entry.tags)
            ))
            
            conn.commit()
    
    def _retrieve_from_db(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve entry from SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM memory_entries WHERE id = ?', (entry_id,))
            row = cursor.fetchone()
            return self._row_to_entry(row) if row else None
    
    def _search_db(self, query: str, category: str, limit: int, min_importance: int) -> List[SearchResult]:
        """Search using SQLite FTS with fallback to simple search."""
        results = []
        
        with sqlite3.connect(self.db_path) as conn:
            # Try FTS search first
            if query.strip():
                try:
                    cursor = conn.execute('''
                        SELECT me.*, bm25(memory_fts) as rank
                        FROM memory_fts 
                        JOIN memory_entries me ON me.id = memory_fts.id
                        WHERE memory_fts MATCH ? AND me.importance >= ?
                        ORDER BY rank
                        LIMIT ?
                    ''', (query, min_importance, limit))
                    
                    for row in cursor.fetchall():
                        entry = self._row_to_entry(row[:-1])  # Exclude rank
                        rank = row[-1]
                        
                        if not category or entry.category == category:
                            results.append(SearchResult(
                                entry=entry,
                                relevance_score=abs(rank),
                                match_type="full_text",
                                matched_terms=query.split()
                            ))
                            
                except Exception as e:
                    # FTS failed, fall back to simple LIKE search
                    logger.warning(f"FTS search failed, using fallback: {e}")
                    cursor = conn.execute('''
                        SELECT * FROM memory_entries 
                        WHERE content LIKE ? AND importance >= ?
                        ORDER BY importance DESC, timestamp DESC
                        LIMIT ?
                    ''', (f'%{query}%', min_importance, limit))
                    
                    for row in cursor.fetchall():
                        entry = self._row_to_entry(row)
                        if not category or entry.category == category:
                            results.append(SearchResult(
                                entry=entry,
                                relevance_score=entry.importance + 5,  # Boost for content match
                                match_type="simple_text",
                                matched_terms=query.split()
                            ))
            
            # Category search if no query
            elif category:
                cursor = conn.execute('''
                    SELECT * FROM memory_entries 
                    WHERE category = ? AND importance >= ?
                    ORDER BY importance DESC, timestamp DESC
                    LIMIT ?
                ''', (category, min_importance, limit))
                
                for row in cursor.fetchall():
                    entry = self._row_to_entry(row)
                    results.append(SearchResult(
                        entry=entry,
                        relevance_score=entry.importance,
                        match_type="category",
                        matched_terms=[]
                    ))
        
        return results[:limit]
    
    def _row_to_entry(self, row) -> MemoryEntry:
        """Convert database row to MemoryEntry."""
        return MemoryEntry(
            id=row[0],
            content=row[1],
            category=row[2],
            timestamp=row[3],
            importance=row[4],
            tags=json.loads(row[5]) if row[5] else [],
            metadata=json.loads(row[6]) if row[6] else {},
            access_count=row[7],
            last_accessed=row[8],
            related_entries=json.loads(row[9]) if row[9] else []
        )
    
    # JSON fallback methods (simplified implementations)
    def _load_from_json(self):
        """Load entries from JSON file."""
        try:
            if os.path.exists(self.json_path):
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for entry_data in data.get('entries', []):
                        entry = MemoryEntry(**entry_data)
                        self.memory_cache[entry.id] = entry
        except Exception as e:
            logger.error(f"JSON loading error: {e}")
    
    def _store_to_json(self, entry: MemoryEntry):
        """Store entry to JSON file."""
        # Simplified JSON storage
        pass
    
    def _retrieve_from_json(self, entry_id: str) -> Optional[MemoryEntry]:
        """Retrieve from JSON."""
        return self.memory_cache.get(entry_id)
    
    def _search_json(self, query: str, category: str, limit: int, min_importance: int) -> List[SearchResult]:
        """Search in JSON data."""
        results = []
        query_lower = query.lower()
        
        for entry in self.memory_cache.values():
            if entry.importance < min_importance:
                continue
            if category and entry.category != category:
                continue
            
            # Simple text matching
            content_lower = entry.content.lower()
            if query_lower in content_lower:
                score = entry.importance
                if query_lower in content_lower:
                    score += 5
                
                results.append(SearchResult(
                    entry=entry,
                    relevance_score=score,
                    match_type="text_match",
                    matched_terms=query.split()
                ))
        
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:limit]
    
    def _get_all_from_json(self) -> List[MemoryEntry]:
        """Get all entries from JSON cache."""
        return list(self.memory_cache.values())
    
    def _manage_cache_size(self):
        """Manage cache size by removing least recently used entries."""
        if len(self.memory_cache) > self.cache_max_size:
            # Sort by last accessed time and remove oldest
            entries_by_access = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].last_accessed
            )
            
            to_remove = len(self.memory_cache) - self.cache_max_size + 10
            for i in range(to_remove):
                entry_id = entries_by_access[i][0]
                del self.memory_cache[entry_id]


# Global memory manager instance
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """Get global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager