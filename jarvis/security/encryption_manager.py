"""
Encryption Manager for Jarvis Security Framework
Enterprise-grade encryption and cryptographic operations
"""

import asyncio
import logging
import secrets
import hashlib
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import base64
import os

logger = logging.getLogger(__name__)

@dataclass
class EncryptionKey:
    """Encryption key metadata"""
    key_id: str
    algorithm: str
    purpose: str  # 'data_encryption', 'file_encryption', 'communication'
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    key_size: int = 256

@dataclass
class EncryptionOperation:
    """Encryption operation record"""
    operation_id: str
    timestamp: datetime
    operation_type: str  # 'encrypt', 'decrypt', 'key_generation', 'key_rotation'
    algorithm: str
    key_id: str
    data_size: int
    success: bool
    user_id: Optional[str] = None

class EncryptionManager:
    """
    Encryption Manager for Enterprise Security Framework
    
    Provides comprehensive encryption capabilities including:
    - Symmetric and asymmetric encryption
    - Key generation and management
    - Data encryption at rest and in transit
    - Cryptographic key rotation
    - Compliance with encryption standards
    - Hardware Security Module (HSM) integration ready
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize encryption manager"""
        self.config = config or {}
        
        # Encryption configuration
        self.default_algorithm = self.config.get('default_algorithm', 'AES-256-GCM')
        self.key_rotation_interval = self.config.get('key_rotation_interval', 30)  # days
        self.enable_key_escrow = self.config.get('enable_key_escrow', False)
        self.require_key_approval = self.config.get('require_key_approval', False)
        
        # Key storage (in production, use HSM or secure key management service)
        self.encryption_keys: Dict[str, EncryptionKey] = {}
        self.key_data: Dict[str, bytes] = {}  # Encrypted key storage
        self.operation_log: List[EncryptionOperation] = []
        
        # Master key for key encryption (KEK - Key Encryption Key)
        self.master_key = self._initialize_master_key()
        
        # Initialize default encryption keys
        self._initialize_default_keys()
        
        logger.info(f"Initialized EncryptionManager with algorithm: {self.default_algorithm}")
    
    def _initialize_master_key(self) -> Fernet:
        """Initialize master key for key encryption"""
        try:
            # In production, this would be from HSM or secure key service
            master_key_material = self.config.get('master_key')
            
            if not master_key_material:
                # Generate new master key
                master_key_material = Fernet.generate_key()
                logger.warning("Generated new master key - ensure this is stored securely!")
            
            if isinstance(master_key_material, str):
                master_key_material = master_key_material.encode()
            
            return Fernet(master_key_material)
            
        except Exception as e:
            logger.error(f"Master key initialization failed: {e}")
            raise
    
    def _initialize_default_keys(self) -> None:
        """Initialize default encryption keys"""
        try:
            # Create default data encryption key
            data_key_id = self._generate_encryption_key(
                purpose='data_encryption',
                algorithm='AES-256-GCM'
            )
            
            # Create default file encryption key
            file_key_id = self._generate_encryption_key(
                purpose='file_encryption',
                algorithm='AES-256-GCM'
            )
            
            # Create default communication encryption key
            comm_key_id = self._generate_encryption_key(
                purpose='communication',
                algorithm='AES-256-GCM'
            )
            
            logger.info(f"Initialized default encryption keys: {data_key_id}, {file_key_id}, {comm_key_id}")
            
        except Exception as e:
            logger.error(f"Default key initialization failed: {e}")
            raise
    
    def _generate_encryption_key(self, purpose: str, algorithm: str) -> str:
        """Generate new encryption key"""
        try:
            key_id = f"{purpose}_{secrets.token_urlsafe(8)}_{datetime.now().strftime('%Y%m%d')}"
            
            # Generate key based on algorithm
            if algorithm.startswith('AES'):
                key_material = secrets.token_bytes(32)  # 256-bit key
            elif algorithm.startswith('RSA'):
                # RSA key pair generation would go here
                key_material = secrets.token_bytes(32)  # Placeholder
            else:
                key_material = secrets.token_bytes(32)  # Default 256-bit
            
            # Encrypt key material with master key
            encrypted_key = self.master_key.encrypt(key_material)
            
            # Create key metadata
            key_metadata = EncryptionKey(
                key_id=key_id,
                algorithm=algorithm,
                purpose=purpose,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(days=self.key_rotation_interval)
            )
            
            # Store key
            self.encryption_keys[key_id] = key_metadata
            self.key_data[key_id] = encrypted_key
            
            # Log key generation
            self._log_encryption_operation(
                'key_generation',
                algorithm,
                key_id,
                len(key_material),
                True
            )
            
            return key_id
            
        except Exception as e:
            logger.error(f"Key generation failed: {e}")
            raise
    
    def _log_encryption_operation(self, operation_type: str, algorithm: str,
                                key_id: str, data_size: int, success: bool,
                                user_id: Optional[str] = None) -> None:
        """Log encryption operation"""
        try:
            operation = EncryptionOperation(
                operation_id=secrets.token_urlsafe(12),
                timestamp=datetime.now(),
                operation_type=operation_type,
                algorithm=algorithm,
                key_id=key_id,
                data_size=data_size,
                success=success,
                user_id=user_id
            )
            
            self.operation_log.append(operation)
            
            # Keep only recent operations in memory
            if len(self.operation_log) > 10000:
                self.operation_log = self.operation_log[-5000:]
                
        except Exception as e:
            logger.error(f"Failed to log encryption operation: {e}")
    
    async def encrypt_data(self, data: Union[str, bytes], key_id: Optional[str] = None,
                          algorithm: Optional[str] = None,
                          user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Encrypt data using specified or default key
        
        Args:
            data: Data to encrypt
            key_id: Encryption key ID (optional, uses default if not specified)
            algorithm: Encryption algorithm (optional)
            user_id: User performing encryption (for audit)
            
        Returns:
            Encryption result with encrypted data and metadata
        """
        try:
            # Convert string to bytes if necessary
            if isinstance(data, str):
                data_bytes = data.encode('utf-8')
            else:
                data_bytes = data
            
            # Get encryption key
            if not key_id:
                key_id = self._get_default_key_for_purpose('data_encryption')
            
            if key_id not in self.encryption_keys:
                raise ValueError(f"Encryption key not found: {key_id}")
            
            key_metadata = self.encryption_keys[key_id]
            
            # Check key expiration
            if key_metadata.expires_at and key_metadata.expires_at < datetime.now():
                logger.warning(f"Using expired key {key_id} - consider key rotation")
            
            # Get decrypted key material
            encrypted_key = self.key_data[key_id]
            key_material = self.master_key.decrypt(encrypted_key)
            
            # Perform encryption based on algorithm
            if key_metadata.algorithm.startswith('AES'):
                encrypted_data, iv = await self._aes_encrypt(data_bytes, key_material)
                encryption_metadata = {
                    'iv': base64.b64encode(iv).decode('utf-8'),
                    'algorithm': key_metadata.algorithm
                }
            else:
                raise ValueError(f"Unsupported encryption algorithm: {key_metadata.algorithm}")
            
            # Log operation
            self._log_encryption_operation(
                'encrypt',
                key_metadata.algorithm,
                key_id,
                len(data_bytes),
                True,
                user_id
            )
            
            result = {
                'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
                'key_id': key_id,
                'algorithm': key_metadata.algorithm,
                'metadata': encryption_metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Data encryption failed: {e}")
            
            # Log failed operation
            if 'key_id' in locals():
                self._log_encryption_operation(
                    'encrypt',
                    algorithm or self.default_algorithm,
                    key_id,
                    len(data_bytes) if 'data_bytes' in locals() else 0,
                    False,
                    user_id
                )
            
            raise
    
    async def decrypt_data(self, encrypted_data: str, key_id: str,
                          metadata: Dict[str, Any],
                          user_id: Optional[str] = None) -> str:
        """
        Decrypt data using specified key
        
        Args:
            encrypted_data: Base64 encoded encrypted data
            key_id: Encryption key ID
            metadata: Encryption metadata
            user_id: User performing decryption (for audit)
            
        Returns:
            Decrypted data as string
        """
        try:
            # Validate key exists
            if key_id not in self.encryption_keys:
                raise ValueError(f"Encryption key not found: {key_id}")
            
            key_metadata = self.encryption_keys[key_id]
            
            # Get decrypted key material
            encrypted_key = self.key_data[key_id]
            key_material = self.master_key.decrypt(encrypted_key)
            
            # Decode encrypted data
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Perform decryption based on algorithm
            if metadata['algorithm'].startswith('AES'):
                iv = base64.b64decode(metadata['iv'].encode('utf-8'))
                decrypted_bytes = await self._aes_decrypt(encrypted_bytes, key_material, iv)
            else:
                raise ValueError(f"Unsupported decryption algorithm: {metadata['algorithm']}")
            
            # Convert back to string
            decrypted_data = decrypted_bytes.decode('utf-8')
            
            # Log operation
            self._log_encryption_operation(
                'decrypt',
                metadata['algorithm'],
                key_id,
                len(encrypted_bytes),
                True,
                user_id
            )
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Data decryption failed: {e}")
            
            # Log failed operation
            self._log_encryption_operation(
                'decrypt',
                metadata.get('algorithm', 'unknown'),
                key_id,
                len(encrypted_data) if encrypted_data else 0,
                False,
                user_id
            )
            
            raise
    
    async def _aes_encrypt(self, data: bytes, key: bytes) -> Tuple[bytes, bytes]:
        """Perform AES encryption"""
        try:
            # Generate random IV
            iv = secrets.token_bytes(16)  # 128-bit IV for AES
            
            # Create cipher
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
            encryptor = cipher.encryptor()
            
            # Encrypt data
            ciphertext = encryptor.update(data) + encryptor.finalize()
            
            # Return ciphertext + auth tag + IV
            return ciphertext + encryptor.tag, iv
            
        except Exception as e:
            logger.error(f"AES encryption failed: {e}")
            raise
    
    async def _aes_decrypt(self, encrypted_data: bytes, key: bytes, iv: bytes) -> bytes:
        """Perform AES decryption"""
        try:
            # Split ciphertext and auth tag
            ciphertext = encrypted_data[:-16]  # All except last 16 bytes
            tag = encrypted_data[-16:]  # Last 16 bytes
            
            # Create cipher
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
            decryptor = cipher.decryptor()
            
            # Decrypt data
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            
            return plaintext
            
        except Exception as e:
            logger.error(f"AES decryption failed: {e}")
            raise
    
    def _get_default_key_for_purpose(self, purpose: str) -> str:
        """Get default key ID for specified purpose"""
        for key_id, key_metadata in self.encryption_keys.items():
            if key_metadata.purpose == purpose and key_metadata.is_active:
                return key_id
        
        raise ValueError(f"No active key found for purpose: {purpose}")
    
    async def rotate_encryption_key(self, key_id: str) -> str:
        """
        Rotate encryption key
        
        Args:
            key_id: Key ID to rotate
            
        Returns:
            New key ID
        """
        try:
            if key_id not in self.encryption_keys:
                raise ValueError(f"Key not found: {key_id}")
            
            old_key = self.encryption_keys[key_id]
            
            # Generate new key with same purpose and algorithm
            new_key_id = self._generate_encryption_key(
                purpose=old_key.purpose,
                algorithm=old_key.algorithm
            )
            
            # Deactivate old key (don't delete for decryption of existing data)
            old_key.is_active = False
            
            # Log key rotation
            self._log_encryption_operation(
                'key_rotation',
                old_key.algorithm,
                f"{key_id}->{new_key_id}",
                0,
                True
            )
            
            logger.info(f"Key rotated: {key_id} -> {new_key_id}")
            
            return new_key_id
            
        except Exception as e:
            logger.error(f"Key rotation failed: {e}")
            raise
    
    async def validate_encryption_compliance(self) -> Dict[str, Any]:
        """
        Validate encryption compliance
        
        Returns:
            Encryption compliance status
        """
        try:
            compliance_score = 100
            compliance_issues = []
            
            # Check key algorithm strength
            weak_algorithms = ['DES', 'RC4', 'MD5']
            for key_id, key_metadata in self.encryption_keys.items():
                if any(weak_alg in key_metadata.algorithm for weak_alg in weak_algorithms):
                    compliance_score -= 20
                    compliance_issues.append(f"Weak encryption algorithm: {key_metadata.algorithm}")
            
            # Check key rotation compliance
            expired_keys = sum(1 for key in self.encryption_keys.values()
                             if key.expires_at and key.expires_at < datetime.now() and key.is_active)
            
            if expired_keys > 0:
                compliance_score -= 15
                compliance_issues.append(f"{expired_keys} expired keys still active")
            
            # Check key size compliance
            for key_id, key_metadata in self.encryption_keys.items():
                if key_metadata.key_size < 256:
                    compliance_score -= 10
                    compliance_issues.append(f"Key size below 256 bits: {key_id}")
            
            # Check operation logging
            recent_operations = [op for op in self.operation_log
                               if op.timestamp > datetime.now() - timedelta(days=1)]
            
            if not recent_operations:
                compliance_score -= 5
                compliance_issues.append("No recent encryption operations logged")
            
            # Check key escrow compliance (if required)
            if self.enable_key_escrow:
                # In real implementation, check if keys are properly escrowed
                pass
            
            return {
                'score': max(0, compliance_score),
                'compliance_level': 'good' if compliance_score >= 80 else 'needs_improvement',
                'issues': compliance_issues,
                'metrics': {
                    'total_keys': len(self.encryption_keys),
                    'active_keys': sum(1 for k in self.encryption_keys.values() if k.is_active),
                    'expired_keys': expired_keys,
                    'recent_operations': len(recent_operations),
                    'algorithms_in_use': list(set(k.algorithm for k in self.encryption_keys.values()))
                }
            }
            
        except Exception as e:
            logger.error(f"Encryption compliance validation failed: {e}")
            return {
                'score': 0,
                'error': str(e)
            }
    
    async def get_encryption_status(self) -> Dict[str, Any]:
        """
        Get encryption system status
        
        Returns:
            Encryption system status
        """
        try:
            active_keys = sum(1 for k in self.encryption_keys.values() if k.is_active)
            total_operations = len(self.operation_log)
            
            recent_operations = [op for op in self.operation_log
                               if op.timestamp > datetime.now() - timedelta(hours=24)]
            
            operation_stats = {
                'encrypt': sum(1 for op in recent_operations if op.operation_type == 'encrypt'),
                'decrypt': sum(1 for op in recent_operations if op.operation_type == 'decrypt'),
                'key_generation': sum(1 for op in recent_operations if op.operation_type == 'key_generation'),
                'key_rotation': sum(1 for op in recent_operations if op.operation_type == 'key_rotation')
            }
            
            return {
                'total_keys': len(self.encryption_keys),
                'active_keys': active_keys,
                'inactive_keys': len(self.encryption_keys) - active_keys,
                'default_algorithm': self.default_algorithm,
                'key_rotation_interval_days': self.key_rotation_interval,
                'total_operations': total_operations,
                'operations_24h': len(recent_operations),
                'operation_breakdown_24h': operation_stats,
                'master_key_status': 'active',
                'key_escrow_enabled': self.enable_key_escrow,
                'configuration': {
                    'default_algorithm': self.default_algorithm,
                    'key_rotation_interval': self.key_rotation_interval,
                    'enable_key_escrow': self.enable_key_escrow,
                    'require_key_approval': self.require_key_approval
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get encryption status: {e}")
            return {'error': str(e)}
    
    async def encrypt_file(self, file_path: str, output_path: Optional[str] = None,
                          key_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Encrypt file
        
        Args:
            file_path: Path to file to encrypt
            output_path: Output path for encrypted file
            key_id: Encryption key ID
            
        Returns:
            File encryption result
        """
        try:
            # Read file data
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Encrypt data
            encryption_result = await self.encrypt_data(file_data, key_id)
            
            # Write encrypted file
            if not output_path:
                output_path = file_path + '.encrypted'
            
            encrypted_file_data = {
                'encrypted_content': encryption_result['encrypted_data'],
                'encryption_metadata': {
                    'key_id': encryption_result['key_id'],
                    'algorithm': encryption_result['algorithm'],
                    'metadata': encryption_result['metadata'],
                    'original_filename': os.path.basename(file_path),
                    'encrypted_at': encryption_result['timestamp']
                }
            }
            
            with open(output_path, 'w') as f:
                json.dump(encrypted_file_data, f, indent=2)
            
            return {
                'success': True,
                'input_file': file_path,
                'output_file': output_path,
                'key_id': encryption_result['key_id'],
                'file_size': len(file_data),
                'encrypted_at': encryption_result['timestamp']
            }
            
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Decrypt file
        
        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Output path for decrypted file
            
        Returns:
            File decryption result
        """
        try:
            
            # Read encrypted file
            with open(encrypted_file_path, 'r') as f:
                encrypted_file_data = json.load(f)
            
            # Extract encryption metadata
            metadata = encrypted_file_data['encryption_metadata']
            
            # Decrypt data
            decrypted_data = await self.decrypt_data(
                encrypted_file_data['encrypted_content'],
                metadata['key_id'],
                metadata['metadata']
            )
            
            # Write decrypted file
            if not output_path:
                original_name = metadata.get('original_filename', 'decrypted_file')
                output_path = os.path.join(
                    os.path.dirname(encrypted_file_path),
                    f"decrypted_{original_name}"
                )
            
            # Convert back to bytes if it was binary data
            if isinstance(decrypted_data, str):
                # Try to detect if it was originally binary
                try:
                    decrypted_bytes = base64.b64decode(decrypted_data)
                    with open(output_path, 'wb') as f:
                        f.write(decrypted_bytes)
                except:
                    with open(output_path, 'w') as f:
                        f.write(decrypted_data)
            else:
                with open(output_path, 'wb') as f:
                    f.write(decrypted_data)
            
            return {
                'success': True,
                'input_file': encrypted_file_path,
                'output_file': output_path,
                'key_id': metadata['key_id'],
                'original_filename': metadata.get('original_filename'),
                'decrypted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }