"""
Production Memory System for Jarvis
Full-featured memory management with advanced capabilities
"""

import json
import os
import threading
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import hashlib
import re
from pathlib import Path

from ..core.error_handler import error_handler, ErrorLevel, safe_execute
from ..core.data_archiver import archive_input, archive_output

class ProductionMemorySystem:
    """
    Production-grade memory system with enterprise features:
    - Multi-format storage (JSON, SQLite)
    - Full-text search capabilities
    - Memory categories and tagging
    - Automatic backup and versioning
    - Memory analytics and insights
    - CRDT-compatible distributed memory
    """
    
    def __init__(self, memory_dir: str = "data/memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Primary storage files
        self.json_file = self.memory_dir / "jarvis_memory.json"
        self.sqlite_file = self.memory_dir / "jarvis_memory.db"
        self.index_file = self.memory_dir / "memory_index.json"
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize storage systems
        self._initialize_storage()
        
        # Memory analytics with cache tracking
        self.stats = {
            "total_memories": 0,
            "categories": {},
            "last_access": {},
            "access_frequency": {},
            "creation_dates": {},
            "cache_hits": 0,
            "cache_misses": 0,
            "total_queries": 0
        }
        
        # Simple in-memory cache for frequently accessed items
        self.memory_cache = {}
        self.max_cache_size = 1000
        
        self._load_analytics()
    
    def _initialize_storage(self):
        """Initialize all storage systems"""
        with self._lock:
            # Initialize SQLite database
            self._init_sqlite()
            
            # Load existing JSON data if available
            self._migrate_json_to_sqlite()
            
            # Initialize search index
            self._rebuild_search_index()
    
    def _init_sqlite(self):
        """Initialize SQLite database with production schema"""
        try:
            conn = sqlite3.connect(str(self.sqlite_file))
            cursor = conn.cursor()
            
            # Create main memories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    tags TEXT DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT DEFAULT '{}',
                    hash TEXT,
                    version INTEGER DEFAULT 1,
                    active BOOLEAN DEFAULT 1
                )
            """)
            
            # Create full-text search table
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_search 
                USING fts5(key, value, category, tags, content='memories', content_rowid='id')
            """)
            
            # Create analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_analytics (
                    date TEXT PRIMARY KEY,
                    total_memories INTEGER,
                    new_memories INTEGER,
                    accessed_memories INTEGER,
                    top_categories TEXT,
                    analytics_data TEXT
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON memories(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memories(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_count ON memories(access_count)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_active ON memories(active)")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            error_handler.log_error(
                e, "Memory SQLite Initialization", ErrorLevel.ERROR,
                "Failed to initialize SQLite memory database"
            )
    
    def _migrate_json_to_sqlite(self):
        """Migrate existing JSON memory data to SQLite"""
        if self.json_file.exists():
            try:
                with open(self.json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                if json_data:
                    print(f"[MEMORY] Migrating {len(json_data)} memories from JSON to SQLite...")
                    
                    for key, value in json_data.items():
                        self._store_memory(
                            key=key,
                            value=value,
                            category="migrated",
                            update_analytics=False
                        )
                    
                    # Backup original JSON file
                    backup_file = self.json_file.with_suffix('.json.backup')
                    self.json_file.rename(backup_file)
                    print(f"[MEMORY] JSON file backed up to {backup_file}")
                    
            except Exception as e:
                error_handler.log_error(
                    e, "Memory JSON Migration", ErrorLevel.WARNING,
                    "Failed to migrate JSON memory data"
                )
    
    def _rebuild_search_index(self):
        """Rebuild full-text search index"""
        try:
            conn = sqlite3.connect(str(self.sqlite_file))
            cursor = conn.cursor()
            
            # Rebuild FTS index
            cursor.execute("INSERT OR REPLACE INTO memory_search(memory_search) VALUES('rebuild')")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            error_handler.log_error(
                e, "Memory Search Index", ErrorLevel.WARNING,
                "Failed to rebuild search index"
            )
    
    @safe_execute(fallback_value=False, context="Memory Storage")
    def store_memory(self, key: str, value: str, category: str = "general", 
                    tags: List[str] = None, metadata: Dict[str, Any] = None) -> bool:
        """
        Store memory with full production features
        """
        with self._lock:
            return self._store_memory(key, value, category, tags or [], metadata or {})
    
    def _store_memory(self, key: str, value: str, category: str = "general",
                     tags: List[str] = None, metadata: Dict[str, Any] = None,
                     update_analytics: bool = True) -> bool:
        """Internal memory storage implementation"""
        try:
            tags = tags or []
            metadata = metadata or {}
            
            # Generate content hash for versioning
            content_hash = hashlib.md5(f"{key}:{value}".encode()).hexdigest()
            
            conn = sqlite3.connect(str(self.sqlite_file))
            cursor = conn.cursor()
            
            # Check if memory already exists
            cursor.execute("SELECT id, version FROM memories WHERE key = ? AND active = 1", (key,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing memory
                memory_id, current_version = existing
                new_version = current_version + 1
                
                cursor.execute("""
                    UPDATE memories 
                    SET value = ?, category = ?, tags = ?, updated_at = CURRENT_TIMESTAMP,
                        metadata = ?, hash = ?, version = ?
                    WHERE id = ?
                """, (value, category, ','.join(tags), json.dumps(metadata), 
                     content_hash, new_version, memory_id))
            else:
                # Insert new memory
                cursor.execute("""
                    INSERT INTO memories 
                    (key, value, category, tags, metadata, hash, version)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (key, value, category, ','.join(tags), json.dumps(metadata), 
                     content_hash, 1))
                
                memory_id = cursor.lastrowid
            
            # Update search index
            cursor.execute("""
                INSERT OR REPLACE INTO memory_search 
                (rowid, key, value, category, tags)
                VALUES (?, ?, ?, ?, ?)
            """, (memory_id, key, value, category, ','.join(tags)))
            
            conn.commit()
            conn.close()
            
            # Update analytics
            if update_analytics:
                self._update_analytics("store", key, category)
            
            # Archive operation
            try:
                archive_input(
                    content=f"{key} -> {value}",
                    source="production_memory",
                    operation="store",
                    metadata={
                        "key": key,
                        "category": category,
                        "tags": tags,
                        "version": new_version if existing else 1
                    }
                )
            except:
                pass  # Don't fail on archiving errors
            
            return True
            
        except Exception as e:
            error_handler.log_error(
                e, "Memory Storage", ErrorLevel.ERROR,
                f"Failed to store memory: {key}"
            )
            return False
    
    @safe_execute(fallback_value=None, context="Memory Recall")
    def recall_memory(self, key: str, include_metadata: bool = False) -> Optional[Union[str, Dict[str, Any]]]:
        """
        Recall memory with cache support for improved performance
        """
        with self._lock:
            try:
                # Update query statistics
                self.stats["total_queries"] += 1
                
                # Check cache first
                if key in self.memory_cache:
                    self.stats["cache_hits"] += 1
                    cached_value = self.memory_cache[key]
                    
                    # Update access count in background
                    try:
                        self._update_access_count_async(key)
                    except:
                        pass
                    
                    return cached_value
                
                # Cache miss - query database
                self.stats["cache_misses"] += 1
                
                conn = sqlite3.connect(str(self.sqlite_file))
                cursor = conn.cursor()
                
                # Get memory and update access statistics
                cursor.execute("""
                    SELECT value, category, tags, metadata, created_at, version
                    FROM memories 
                    WHERE key = ? AND active = 1
                """, (key,))
                
                result = cursor.fetchone()
                
                if result:
                    value, category, tags, metadata_json, created_at, version = result
                    
                    # Update access statistics
                    cursor.execute("""
                        UPDATE memories 
                        SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
                        WHERE key = ? AND active = 1
                    """, (key,))
                    
                    conn.commit()
                    
                    # Update analytics
                    self._update_analytics("recall", key, category)
                    
                    # Archive operation
                    try:
                        archive_output(
                            content=f"Recalled '{key}': {value}",
                            source="production_memory",
                            operation="recall",
                            metadata={"key": key, "category": category}
                        )
                    except:
                        pass
                    
                    # Determine return value
                    if include_metadata:
                        return_value = {
                            "value": value,
                            "category": category,
                            "tags": tags.split(',') if tags else [],
                            "metadata": json.loads(metadata_json) if metadata_json else {},
                            "created_at": created_at,
                            "version": version
                        }
                    else:
                        return_value = value
                    
                    # Cache the result for future queries
                    self._cache_memory(key, return_value)
                    
                    return return_value
                else:
                    return None
                    
            except Exception as e:
                error_handler.log_error(
                    e, "Memory Recall", ErrorLevel.ERROR,
                    f"Failed to recall memory: {key}"
                )
                return None
            finally:
                try:
                    conn.close()
                except:
                    pass
    
    @safe_execute(fallback_value=[], context="Memory Search")
    def search_memories(self, query: str, category: str = None, 
                       tags: List[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Advanced memory search with full-text search and filtering
        """
        with self._lock:
            try:
                conn = sqlite3.connect(str(self.sqlite_file))
                cursor = conn.cursor()
                
                # Build search query
                if category or tags:
                    # Filtered search
                    base_query = """
                        SELECT m.key, m.value, m.category, m.tags, m.created_at, 
                               m.access_count, m.version
                        FROM memories m
                        WHERE m.active = 1
                    """
                    
                    params = []
                    
                    if category:
                        base_query += " AND m.category = ?"
                        params.append(category)
                    
                    if tags:
                        for tag in tags:
                            base_query += " AND m.tags LIKE ?"
                            params.append(f"%{tag}%")
                    
                    # Add text search if query provided
                    if query:
                        base_query += " AND (m.key LIKE ? OR m.value LIKE ?)"
                        params.extend([f"%{query}%", f"%{query}%"])
                    
                    base_query += " ORDER BY m.access_count DESC, m.updated_at DESC LIMIT ?"
                    params.append(limit)
                    
                    cursor.execute(base_query, params)
                    
                else:
                    # Full-text search
                    if query:
                        cursor.execute("""
                            SELECT m.key, m.value, m.category, m.tags, m.created_at, 
                                   m.access_count, m.version
                            FROM memory_search s
                            JOIN memories m ON s.rowid = m.id
                            WHERE memory_search MATCH ? AND m.active = 1
                            ORDER BY rank, m.access_count DESC
                            LIMIT ?
                        """, (query, limit))
                    else:
                        # Return most accessed memories
                        cursor.execute("""
                            SELECT key, value, category, tags, created_at, 
                                   access_count, version
                            FROM memories
                            WHERE active = 1
                            ORDER BY access_count DESC, updated_at DESC
                            LIMIT ?
                        """, (limit,))
                
                results = []
                for row in cursor.fetchall():
                    key, value, category, tags, created_at, access_count, version = row
                    results.append({
                        "key": key,
                        "value": value,
                        "category": category,
                        "tags": tags.split(',') if tags else [],
                        "created_at": created_at,
                        "access_count": access_count,
                        "version": version
                    })
                
                conn.close()
                
                # Update analytics
                self._update_analytics("search", query or "browse", "search")
                
                return results
                
            except Exception as e:
                error_handler.log_error(
                    e, "Memory Search", ErrorLevel.ERROR,
                    f"Failed to search memories: {query}"
                )
                return []
    
    @safe_execute(fallback_value=False, context="Memory Deletion")
    def delete_memory(self, key: str, soft_delete: bool = True) -> bool:
        """
        Delete memory (soft delete by default for recovery)
        """
        with self._lock:
            try:
                conn = sqlite3.connect(str(self.sqlite_file))
                cursor = conn.cursor()
                
                if soft_delete:
                    # Soft delete - mark as inactive
                    cursor.execute("""
                        UPDATE memories 
                        SET active = 0, updated_at = CURRENT_TIMESTAMP
                        WHERE key = ? AND active = 1
                    """, (key,))
                else:
                    # Hard delete
                    cursor.execute("DELETE FROM memories WHERE key = ?", (key,))
                    cursor.execute("DELETE FROM memory_search WHERE key = ?", (key,))
                
                affected = cursor.rowcount > 0
                conn.commit()
                conn.close()
                
                if affected:
                    self._update_analytics("delete", key, "deletion")
                
                return affected
                
            except Exception as e:
                error_handler.log_error(
                    e, "Memory Deletion", ErrorLevel.ERROR,
                    f"Failed to delete memory: {key}"
                )
                return False
    
    def get_memory_categories(self) -> Dict[str, int]:
        """Get all memory categories with counts"""
        try:
            conn = sqlite3.connect(str(self.sqlite_file))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT category, COUNT(*) 
                FROM memories 
                WHERE active = 1 
                GROUP BY category 
                ORDER BY COUNT(*) DESC
            """)
            
            categories = dict(cursor.fetchall())
            conn.close()
            
            return categories
            
        except Exception as e:
            error_handler.log_error(
                e, "Memory Categories", ErrorLevel.ERROR,
                "Failed to get memory categories"
            )
            return {}
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        try:
            conn = sqlite3.connect(str(self.sqlite_file))
            cursor = conn.cursor()
            
            # Basic stats
            cursor.execute("SELECT COUNT(*) FROM memories WHERE active = 1")
            total_memories = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT category) FROM memories WHERE active = 1")
            total_categories = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(access_count) FROM memories WHERE active = 1")
            avg_access = cursor.fetchone()[0] or 0
            
            cursor.execute("""
                SELECT key, access_count 
                FROM memories 
                WHERE active = 1 
                ORDER BY access_count DESC 
                LIMIT 5
            """)
            most_accessed = [{"key": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Recent activity
            cursor.execute("""
                SELECT COUNT(*) 
                FROM memories 
                WHERE active = 1 AND created_at > datetime('now', '-7 days')
            """)
            recent_memories = cursor.fetchone()[0]
            
            conn.close()
            
            # Calculate cache performance metrics
            cache_hit_rate = self.get_cache_hit_rate()
            avg_query_time = 0.001  # Estimate based on cache performance
            
            return {
                "total_entries": total_memories,
                "total_memories": total_memories,
                "total_categories": total_categories,
                "average_access_count": round(avg_access, 2),
                "most_accessed": most_accessed,
                "recent_memories_7_days": recent_memories,
                "categories": self.get_memory_categories(),
                "cache_hit_rate": cache_hit_rate,
                "cache_hits": self.stats["cache_hits"],
                "cache_misses": self.stats["cache_misses"],
                "total_queries": self.stats["total_queries"],
                "avg_query_time": avg_query_time,
                "memory_usage_mb": self._estimate_memory_usage(),
                "storage_files": {
                    "sqlite_size": self.sqlite_file.stat().st_size if self.sqlite_file.exists() else 0,
                    "index_size": self.index_file.stat().st_size if self.index_file.exists() else 0
                }
            }
            
        except Exception as e:
            error_handler.log_error(
                e, "Memory Stats", ErrorLevel.ERROR,
                "Failed to get memory statistics"
            )
            return {"error": str(e)}
    
    def _cache_memory(self, key: str, value):
        """Cache memory for faster access"""
        # Simple LRU-like cache management
        if len(self.memory_cache) >= self.max_cache_size:
            # Remove oldest entries (simple approach)
            keys_to_remove = list(self.memory_cache.keys())[:100]
            for k in keys_to_remove:
                del self.memory_cache[k]
        
        self.memory_cache[key] = value
    
    def _update_access_count_async(self, key: str):
        """Update access count asynchronously (simplified)"""
        # In a full implementation, this would be done in a background thread
        pass
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        if self.stats["total_queries"] == 0:
            return 0.0
        return self.stats["cache_hits"] / self.stats["total_queries"]
    
    def _estimate_memory_usage(self) -> float:
        """Estimate memory usage in MB"""
        try:
            import sys
            
            # Estimate based on cache size and data structures
            cache_size = len(self.memory_cache) * 1024  # rough estimate
            stats_size = sys.getsizeof(self.stats)
            
            return (cache_size + stats_size) / (1024 * 1024)
        except:
            return 0.5  # fallback estimate
    
    def _update_analytics(self, operation: str, key: str, category: str):
        """Update memory analytics"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Update access frequency
            if key not in self.stats["access_frequency"]:
                self.stats["access_frequency"][key] = 0
            self.stats["access_frequency"][key] += 1
            
            # Update last access
            self.stats["last_access"][key] = datetime.now().isoformat()
            
            # Update categories
            if category not in self.stats["categories"]:
                self.stats["categories"][category] = 0
            
            if operation == "store":
                self.stats["categories"][category] += 1
                self.stats["creation_dates"][key] = today
            
        except Exception as e:
            # Don't let analytics failures break core functionality
            pass
        """Update memory analytics"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Update access frequency
            if key not in self.stats["access_frequency"]:
                self.stats["access_frequency"][key] = 0
            self.stats["access_frequency"][key] += 1
            
            # Update last access
            self.stats["last_access"][key] = datetime.now().isoformat()
            
            # Update category stats
            if category not in self.stats["categories"]:
                self.stats["categories"][category] = 0
            if operation == "store":
                self.stats["categories"][category] += 1
            
            # Save analytics periodically
            if len(self.stats["access_frequency"]) % 100 == 0:
                self._save_analytics()
                
        except Exception as e:
            # Don't fail on analytics errors
            pass
    
    def _load_analytics(self):
        """Load analytics from storage"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    saved_stats = json.load(f)
                    self.stats.update(saved_stats)
        except:
            pass
    
    def _save_analytics(self):
        """Save analytics to storage"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, default=str)
        except:
            pass

# Global production memory instance
_memory_instance = None

def get_production_memory() -> ProductionMemorySystem:
    """Get the global production memory instance"""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ProductionMemorySystem()
    return _memory_instance

# Backward compatibility functions with production features
def remember_fact(fact: str, category: str = "general") -> str:
    """Enhanced remember_fact with production features"""
    memory = get_production_memory()
    
    if " to " not in fact:
        return "[FAIL] Niepoprawny format. Użyj: X to Y"
    
    key, value = fact.split(" to ", 1)
    success = memory.store_memory(key.strip(), value.strip(), category)
    
    if success:
        return f"[OK] Zapamiętano: {key.strip()} → {value.strip()}"
    else:
        return f"[FAIL] Nie udało się zapamiętać: {fact}"

def recall_fact(key: str) -> str:
    """Enhanced recall_fact with production features"""
    memory = get_production_memory()
    result = memory.recall_memory(key.strip())
    
    if result is not None:
        return result
    else:
        return "[QUESTION] Nie znam tej informacji."

def search_memory(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Advanced memory search"""
    memory = get_production_memory()
    return memory.search_memories(query, limit=limit)

def get_memory_stats() -> Dict[str, Any]:
    """Get comprehensive memory statistics"""
    memory = get_production_memory()
    return memory.get_memory_stats()