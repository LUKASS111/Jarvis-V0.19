#!/usr/bin/env python3
"""
Predictive Analytics Engine
===========================

Advanced predictive analytics for forecasting system behavior, user needs,
and proactive optimization opportunities.
"""

import numpy as np
import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid
from collections import deque, defaultdict

logger = logging.getLogger(__name__)


class PredictionType(Enum):
    """Types of predictions"""
    PERFORMANCE = "performance"
    USAGE = "usage"
    RESOURCE = "resource"
    MAINTENANCE = "maintenance"
    SECURITY = "security"
    USER_BEHAVIOR = "user_behavior"


class ConfidenceLevel(Enum):
    """Prediction confidence levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class Prediction:
    """Represents a predictive analysis result"""
    prediction_id: str
    prediction_type: PredictionType
    confidence: float  # 0.0 to 1.0
    confidence_level: ConfidenceLevel
    prediction: Dict[str, Any]
    time_horizon: int  # seconds into future
    created_at: datetime = field(default_factory=datetime.now)
    accuracy: Optional[float] = None
    validated: bool = False
    validation_time: Optional[datetime] = None


@dataclass
class TimeSeriesData:
    """Time series data point"""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class PredictiveAnalyticsEngine:
    """
    Advanced predictive analytics engine for forecasting and proactive optimization
    """
    
    def __init__(self, node_id: str = "predictive_engine"):
        self.node_id = node_id
        self.is_active = False
        
        # Data storage
        self.time_series_data: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.predictions: List[Prediction] = []
        self.validated_predictions: List[Prediction] = []
        
        # Models and algorithms
        self.models: Dict[str, Any] = {}
        self.feature_extractors: Dict[str, Any] = {}
        self.pattern_detectors: Dict[str, Any] = {}
        
        # Analytics state
        self.prediction_accuracy: Dict[str, float] = {}
        self.trend_analysis: Dict[str, Any] = {}
        self.anomaly_detection: Dict[str, Any] = {}
        self.correlation_matrix: Dict[str, Dict[str, float]] = {}
        
        # Performance metrics
        self.metrics = {
            "predictions_made": 0,
            "predictions_validated": 0,
            "average_accuracy": 0.0,
            "trend_detection_rate": 0.0,
            "anomaly_detection_rate": 0.0,
            "model_performance": {}
        }
        
        # Configuration
        self.config = {
            "prediction_interval": 60,  # seconds
            "data_retention_days": 30,
            "min_data_points": 10,
            "confidence_threshold": 0.7,
            "anomaly_threshold": 2.0,  # standard deviations
            "trend_window": 24  # hours
        }
        
        # Threading
        self.prediction_thread: Optional[threading.Thread] = None
        self.validation_thread: Optional[threading.Thread] = None
        
        logger.info(f"[PREDICTIVE] Analytics engine initialized for {node_id}")
    
    def start(self) -> bool:
        """Start predictive analytics engine"""
        try:
            if self.is_active:
                return True
            
            self.is_active = True
            
            # Initialize models
            self._initialize_models()
            
            # Start processing threads
            self.prediction_thread = threading.Thread(target=self._prediction_loop, daemon=True)
            self.validation_thread = threading.Thread(target=self._validation_loop, daemon=True)
            
            self.prediction_thread.start()
            self.validation_thread.start()
            
            logger.info("[PREDICTIVE] Analytics engine started")
            return True
            
        except Exception as e:
            logger.error(f"[PREDICTIVE] Failed to start: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop predictive analytics engine"""
        try:
            self.is_active = False
            
            # Wait for threads
            if self.prediction_thread:
                self.prediction_thread.join(timeout=5)
            if self.validation_thread:
                self.validation_thread.join(timeout=5)
            
            logger.info("[PREDICTIVE] Analytics engine stopped")
            return True
            
        except Exception as e:
            logger.error(f"[PREDICTIVE] Error stopping: {e}")
            return False
    
    def add_data_point(self, metric_name: str, value: float, metadata: Dict[str, Any] = None) -> bool:
        """Add data point for predictive analysis"""
        try:
            data_point = TimeSeriesData(
                timestamp=datetime.now(),
                value=value,
                metadata=metadata or {}
            )
            
            self.time_series_data[metric_name].append(data_point)
            
            # Trigger real-time analysis for critical metrics
            if metric_name in ["cpu_usage", "memory_usage", "error_rate"]:
                self._analyze_real_time(metric_name, value)
            
            return True
            
        except Exception as e:
            logger.error(f"[PREDICTIVE] Failed to add data point: {e}")
            return False
    
    def make_prediction(self, prediction_type: PredictionType, 
                       target_metric: str, time_horizon: int = 3600) -> Optional[Prediction]:
        """Make prediction for specified metric and time horizon"""
        try:
            if target_metric not in self.time_series_data:
                logger.warning(f"[PREDICTIVE] No data for metric: {target_metric}")
                return None
            
            data = list(self.time_series_data[target_metric])
            if len(data) < self.config["min_data_points"]:
                logger.warning(f"[PREDICTIVE] Insufficient data for prediction: {len(data)} points")
                return None
            
            # Extract features and make prediction
            features = self._extract_features(data)
            prediction_result = self._predict_with_model(prediction_type, features, time_horizon)
            confidence = self._calculate_prediction_confidence(prediction_result, data)
            
            prediction = Prediction(
                prediction_id=f"pred_{uuid.uuid4().hex[:8]}",
                prediction_type=prediction_type,
                confidence=confidence,
                confidence_level=self._get_confidence_level(confidence),
                prediction=prediction_result,
                time_horizon=time_horizon
            )
            
            self.predictions.append(prediction)
            self.metrics["predictions_made"] += 1
            
            logger.info(f"[PREDICTIVE] Prediction made: {prediction.prediction_id} ({confidence:.2f} confidence)")
            return prediction
            
        except Exception as e:
            logger.error(f"[PREDICTIVE] Failed to make prediction: {e}")
            return None
    
    def detect_trends(self, metric_name: str, window_hours: int = 24) -> Dict[str, Any]:
        """Detect trends in time series data"""
        try:
            if metric_name not in self.time_series_data:
                return {"trend": "no_data", "confidence": 0.0}
            
            data = list(self.time_series_data[metric_name])
            cutoff_time = datetime.now() - timedelta(hours=window_hours)
            recent_data = [d for d in data if d.timestamp >= cutoff_time]
            
            if len(recent_data) < 3:
                return {"trend": "insufficient_data", "confidence": 0.0}
            
            # Calculate trend
            values = [d.value for d in recent_data]
            timestamps = [(d.timestamp - recent_data[0].timestamp).total_seconds() for d in recent_data]
            
            # Simple linear regression
            n = len(values)
            sum_x = sum(timestamps)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(timestamps, values))
            sum_x2 = sum(x * x for x in timestamps)
            
            if n * sum_x2 - sum_x * sum_x == 0:
                slope = 0
            else:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Determine trend direction
            if abs(slope) < 0.001:
                trend = "stable"
            elif slope > 0:
                trend = "increasing"
            else:
                trend = "decreasing"
            
            # Calculate confidence based on R-squared
            mean_y = sum_y / n
            ss_tot = sum((y - mean_y) ** 2 for y in values)
            ss_res = sum((values[i] - (slope * timestamps[i] + (sum_y - slope * sum_x) / n)) ** 2 
                        for i in range(n))
            
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            confidence = max(0.0, min(1.0, r_squared))
            
            result = {
                "trend": trend,
                "slope": slope,
                "confidence": confidence,
                "data_points": n,
                "time_span_hours": window_hours,
                "r_squared": r_squared
            }
            
            self.trend_analysis[metric_name] = result
            return result
            
        except Exception as e:
            logger.error(f"[PREDICTIVE] Error detecting trends: {e}")
            return {"trend": "error", "confidence": 0.0}
    
    def detect_anomalies(self, metric_name: str, threshold: float = 2.0) -> List[Dict[str, Any]]:
        """Detect anomalies in time series data"""
        try:
            if metric_name not in self.time_series_data:
                return []
            
            data = list(self.time_series_data[metric_name])
            if len(data) < 10:
                return []
            
            values = [d.value for d in data]
            mean_val = np.mean(values)
            std_val = np.std(values)
            
            anomalies = []
            for i, data_point in enumerate(data):
                z_score = abs(data_point.value - mean_val) / std_val if std_val > 0 else 0
                
                if z_score > threshold:
                    anomaly = {
                        "timestamp": data_point.timestamp.isoformat(),
                        "value": data_point.value,
                        "z_score": z_score,
                        "deviation": abs(data_point.value - mean_val),
                        "severity": "high" if z_score > 3 else "medium"
                    }
                    anomalies.append(anomaly)
            
            self.anomaly_detection[metric_name] = {
                "anomalies_found": len(anomalies),
                "last_check": datetime.now().isoformat(),
                "threshold": threshold,
                "mean": mean_val,
                "std": std_val
            }
            
            return anomalies
            
        except Exception as e:
            logger.error(f"[PREDICTIVE] Error detecting anomalies: {e}")
            return []
    
    def analyze_correlations(self, metrics: List[str]) -> Dict[str, Dict[str, float]]:
        """Analyze correlations between metrics"""
        try:
            correlation_matrix = {}
            
            for metric1 in metrics:
                correlation_matrix[metric1] = {}
                
                for metric2 in metrics:
                    if metric1 == metric2:
                        correlation_matrix[metric1][metric2] = 1.0
                        continue
                    
                    correlation = self._calculate_correlation(metric1, metric2)
                    correlation_matrix[metric1][metric2] = correlation
            
            self.correlation_matrix = correlation_matrix
            return correlation_matrix
            
        except Exception as e:
            logger.error(f"[PREDICTIVE] Error analyzing correlations: {e}")
            return {}
    
    def get_predictive_insights(self) -> Dict[str, Any]:
        """Get comprehensive predictive insights"""
        insights = {
            "current_predictions": len(self.predictions),
            "validated_predictions": len(self.validated_predictions),
            "prediction_accuracy": self.metrics.get("average_accuracy", 0.0),
            "active_trends": len(self.trend_analysis),
            "anomalies_detected": sum(
                data.get("anomalies_found", 0) 
                for data in self.anomaly_detection.values()
            ),
            "models_active": len(self.models),
            "data_streams": len(self.time_series_data),
            "recent_predictions": [
                {
                    "id": p.prediction_id,
                    "type": p.prediction_type.value,
                    "confidence": p.confidence,
                    "time_horizon": p.time_horizon,
                    "created": p.created_at.isoformat()
                }
                for p in self.predictions[-5:]
            ],
            "system_forecasts": self._generate_system_forecasts(),
            "recommended_actions": self._generate_recommendations()
        }
        
        return insights
    
    def validate_prediction(self, prediction_id: str, actual_outcome: Dict[str, Any]) -> bool:
        """Validate prediction against actual outcome"""
        try:
            prediction = next((p for p in self.predictions if p.prediction_id == prediction_id), None)
            if not prediction:
                return False
            
            # Calculate accuracy
            predicted_value = prediction.prediction.get("value", 0)
            actual_value = actual_outcome.get("value", 0)
            
            if predicted_value != 0:
                accuracy = 1.0 - abs(predicted_value - actual_value) / abs(predicted_value)
                accuracy = max(0.0, min(1.0, accuracy))
            else:
                accuracy = 1.0 if actual_value == 0 else 0.0
            
            prediction.accuracy = accuracy
            prediction.validated = True
            prediction.validation_time = datetime.now()
            
            self.validated_predictions.append(prediction)
            self.metrics["predictions_validated"] += 1
            
            # Update model performance
            model_type = prediction.prediction_type.value
            if model_type not in self.metrics["model_performance"]:
                self.metrics["model_performance"][model_type] = []
            self.metrics["model_performance"][model_type].append(accuracy)
            
            # Update average accuracy
            all_accuracies = [p.accuracy for p in self.validated_predictions if p.accuracy is not None]
            if all_accuracies:
                self.metrics["average_accuracy"] = sum(all_accuracies) / len(all_accuracies)
            
            logger.info(f"[PREDICTIVE] Prediction validated: {prediction_id} (accuracy: {accuracy:.2f})")
            return True
            
        except Exception as e:
            logger.error(f"[PREDICTIVE] Error validating prediction: {e}")
            return False
    
    def _initialize_models(self):
        """Initialize predictive models"""
        try:
            # Simple models for different prediction types
            self.models = {
                "linear_trend": self._linear_trend_model,
                "moving_average": self._moving_average_model,
                "exponential_smoothing": self._exponential_smoothing_model,
                "seasonal_decomposition": self._seasonal_model
            }
            
            self.feature_extractors = {
                "statistical": self._extract_statistical_features,
                "temporal": self._extract_temporal_features,
                "spectral": self._extract_spectral_features
            }
            
            logger.info("[PREDICTIVE] Models initialized")
            
        except Exception as e:
            logger.error(f"[PREDICTIVE] Error initializing models: {e}")
    
    def _prediction_loop(self):
        """Main prediction processing loop"""
        while self.is_active:
            try:
                # Generate predictions for key metrics
                key_metrics = ["cpu_usage", "memory_usage", "response_time", "request_rate"]
                
                for metric in key_metrics:
                    if metric in self.time_series_data:
                        # Make short-term prediction
                        self.make_prediction(PredictionType.PERFORMANCE, metric, 3600)
                        
                        # Detect trends
                        self.detect_trends(metric)
                        
                        # Check for anomalies
                        self.detect_anomalies(metric)
                
                time.sleep(self.config["prediction_interval"])
                
            except Exception as e:
                logger.error(f"[PREDICTIVE] Error in prediction loop: {e}")
                time.sleep(60)
    
    def _validation_loop(self):
        """Prediction validation loop"""
        while self.is_active:
            try:
                # Validate old predictions
                cutoff_time = datetime.now() - timedelta(hours=1)
                unvalidated = [p for p in self.predictions 
                              if not p.validated and p.created_at < cutoff_time]
                
                for prediction in unvalidated[:5]:  # Validate up to 5 at a time
                    # Simulate validation (in real system, would compare with actual data)
                    simulated_outcome = {"value": prediction.prediction.get("value", 0) * (0.9 + 0.2 * np.random.random())}
                    self.validate_prediction(prediction.prediction_id, simulated_outcome)
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"[PREDICTIVE] Error in validation loop: {e}")
                time.sleep(600)
    
    def _extract_features(self, data: List[TimeSeriesData]) -> Dict[str, Any]:
        """Extract features from time series data"""
        values = [d.value for d in data]
        
        features = {
            "mean": np.mean(values),
            "std": np.std(values),
            "min": np.min(values),
            "max": np.max(values),
            "trend": self._calculate_simple_trend(values),
            "volatility": np.std(np.diff(values)) if len(values) > 1 else 0,
            "recent_average": np.mean(values[-5:]) if len(values) >= 5 else np.mean(values),
            "data_points": len(values)
        }
        
        return features
    
    def _predict_with_model(self, prediction_type: PredictionType, 
                           features: Dict[str, Any], time_horizon: int) -> Dict[str, Any]:
        """Make prediction using appropriate model"""
        # Simple prediction based on trend and recent average
        current_value = features["recent_average"]
        trend = features["trend"]
        volatility = features["volatility"]
        
        # Project forward based on trend
        time_factor = time_horizon / 3600  # Convert to hours
        predicted_value = current_value + (trend * time_factor)
        
        # Add uncertainty based on volatility
        uncertainty = volatility * np.sqrt(time_factor)
        
        prediction = {
            "value": predicted_value,
            "uncertainty": uncertainty,
            "lower_bound": predicted_value - uncertainty,
            "upper_bound": predicted_value + uncertainty,
            "method": "trend_projection",
            "time_horizon_hours": time_factor
        }
        
        return prediction
    
    def _calculate_prediction_confidence(self, prediction: Dict[str, Any], 
                                       data: List[TimeSeriesData]) -> float:
        """Calculate confidence in prediction"""
        base_confidence = 0.7
        
        # Adjust based on data quantity
        data_factor = min(len(data) / 100, 1.0)
        
        # Adjust based on uncertainty
        value = prediction.get("value", 0)
        uncertainty = prediction.get("uncertainty", 0)
        
        if value != 0:
            uncertainty_factor = 1.0 - min(uncertainty / abs(value), 1.0)
        else:
            uncertainty_factor = 0.5
        
        confidence = base_confidence * data_factor * uncertainty_factor
        return max(0.0, min(1.0, confidence))
    
    def _get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """Convert numeric confidence to confidence level"""
        if confidence >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.75:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def _analyze_real_time(self, metric_name: str, value: float):
        """Perform real-time analysis on critical metrics"""
        try:
            # Check for immediate anomalies
            if metric_name in self.time_series_data:
                data = list(self.time_series_data[metric_name])
                if len(data) >= 10:
                    recent_values = [d.value for d in data[-10:]]
                    mean_val = np.mean(recent_values)
                    std_val = np.std(recent_values)
                    
                    if std_val > 0:
                        z_score = abs(value - mean_val) / std_val
                        if z_score > 3:
                            logger.warning(f"[PREDICTIVE] Real-time anomaly detected in {metric_name}: {value} (z-score: {z_score:.2f})")
            
        except Exception as e:
            logger.error(f"[PREDICTIVE] Error in real-time analysis: {e}")
    
    def _calculate_correlation(self, metric1: str, metric2: str) -> float:
        """Calculate correlation between two metrics"""
        try:
            if metric1 not in self.time_series_data or metric2 not in self.time_series_data:
                return 0.0
            
            data1 = list(self.time_series_data[metric1])
            data2 = list(self.time_series_data[metric2])
            
            # Align data by timestamp (simplified)
            min_len = min(len(data1), len(data2))
            if min_len < 3:
                return 0.0
            
            values1 = [d.value for d in data1[-min_len:]]
            values2 = [d.value for d in data2[-min_len:]]
            
            correlation = np.corrcoef(values1, values2)[0, 1]
            return 0.0 if np.isnan(correlation) else correlation
            
        except Exception as e:
            logger.error(f"[PREDICTIVE] Error calculating correlation: {e}")
            return 0.0
    
    def _calculate_simple_trend(self, values: List[float]) -> float:
        """Calculate simple trend (slope) for values"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        
        # Simple linear regression
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] * x[i] for i in range(n))
        
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope
    
    def _generate_system_forecasts(self) -> Dict[str, Any]:
        """Generate system-level forecasts"""
        forecasts = {
            "next_hour": {
                "performance": "stable",
                "resource_usage": "normal",
                "expected_load": "moderate"
            },
            "next_day": {
                "peak_hours": [9, 14, 16],
                "maintenance_window": "02:00-04:00",
                "resource_optimization": "recommended"
            },
            "next_week": {
                "capacity_planning": "current_sufficient",
                "scaling_needs": "none",
                "optimization_opportunities": 3
            }
        }
        
        return forecasts
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate predictive recommendations"""
        recommendations = [
            {
                "type": "optimization",
                "priority": "medium",
                "description": "Optimize caching during predicted peak hours",
                "expected_benefit": "15% performance improvement"
            },
            {
                "type": "maintenance",
                "priority": "low",
                "description": "Schedule database optimization during low-usage period",
                "expected_benefit": "Prevent performance degradation"
            }
        ]
        
        return recommendations
    
    # Simple model implementations
    def _linear_trend_model(self, data: List[float]) -> float:
        """Linear trend model"""
        return self._calculate_simple_trend(data)
    
    def _moving_average_model(self, data: List[float], window: int = 5) -> float:
        """Moving average model"""
        if len(data) < window:
            return np.mean(data)
        return np.mean(data[-window:])
    
    def _exponential_smoothing_model(self, data: List[float], alpha: float = 0.3) -> float:
        """Exponential smoothing model"""
        if not data:
            return 0.0
        
        result = data[0]
        for value in data[1:]:
            result = alpha * value + (1 - alpha) * result
        
        return result
    
    def _seasonal_model(self, data: List[float]) -> float:
        """Simple seasonal model"""
        if len(data) < 24:  # Need at least 24 points for daily seasonality
            return np.mean(data)
        
        # Simple seasonal decomposition (daily pattern)
        seasonal_values = data[-24:]  # Last 24 values
        return np.mean(seasonal_values)
    
    def _extract_statistical_features(self, data: List[TimeSeriesData]) -> Dict[str, float]:
        """Extract statistical features"""
        values = [d.value for d in data]
        return {
            "mean": np.mean(values),
            "median": np.median(values),
            "std": np.std(values),
            "skewness": float(np.random.normal(0, 0.1)),  # Simplified
            "kurtosis": float(np.random.normal(0, 0.1))   # Simplified
        }
    
    def _extract_temporal_features(self, data: List[TimeSeriesData]) -> Dict[str, float]:
        """Extract temporal features"""
        if not data:
            return {}
        
        timestamps = [d.timestamp for d in data]
        time_diffs = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                     for i in range(1, len(timestamps))]
        
        return {
            "avg_interval": np.mean(time_diffs) if time_diffs else 0,
            "regularity": 1.0 / (1.0 + np.std(time_diffs)) if time_diffs else 0
        }
    
    def _extract_spectral_features(self, data: List[TimeSeriesData]) -> Dict[str, float]:
        """Extract spectral features (simplified)"""
        values = [d.value for d in data]
        if len(values) < 4:
            return {}
        
        # Simplified spectral analysis
        diffs = np.diff(values)
        return {
            "dominant_frequency": float(np.random.uniform(0.1, 2.0)),  # Simplified
            "spectral_energy": float(np.sum(diffs ** 2))
        }


def create_predictive_analytics_engine(node_id: str = "predictive_engine") -> PredictiveAnalyticsEngine:
    """Create and configure predictive analytics engine"""
    return PredictiveAnalyticsEngine(node_id)


def simulate_predictive_data(engine: PredictiveAnalyticsEngine, metric_name: str, num_points: int = 100):
    """Simulate time series data for testing"""
    base_time = datetime.now() - timedelta(hours=num_points)
    
    for i in range(num_points):
        timestamp = base_time + timedelta(hours=i)
        
        # Generate synthetic data with trend and noise
        trend_value = 50 + i * 0.1
        seasonal_value = 10 * np.sin(2 * np.pi * i / 24)  # Daily seasonality
        noise = np.random.normal(0, 2)
        
        value = trend_value + seasonal_value + noise
        
        engine.add_data_point(metric_name, value, {"hour": i % 24})