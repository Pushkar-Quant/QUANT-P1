"""
Production Monitoring and Logging System

Provides comprehensive monitoring for:
- Performance metrics
- System health
- Error tracking
- Real-time alerts
"""

import logging
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import numpy as np


@dataclass
class PerformanceMetrics:
    """Real-time performance metrics."""
    timestamp: float
    pnl: float
    inventory: int
    sharpe_ratio: float
    drawdown: float
    num_trades: int
    latency_ms: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


class MonitoringSystem:
    """
    Comprehensive monitoring system for production deployment.
    
    Features:
    - Real-time metrics collection
    - Log aggregation
    - Alert management
    - Performance tracking
    """
    
    def __init__(self, log_dir: str = "logs", metrics_file: str = "metrics.jsonl"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self.metrics_file = self.log_dir / metrics_file
        self.logger = self._setup_logging()
        
        # Performance tracking
        self.start_time = time.time()
        self.metrics_buffer = []
        self.alert_thresholds = {
            'max_drawdown': 0.20,
            'max_inventory': 1000,
            'min_sharpe': -0.5,
            'max_latency_ms': 100
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Configure logging system."""
        logger = logging.getLogger('ALPE_Monitor')
        logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(self.log_dir / 'application.log')
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def log_metrics(self, metrics: PerformanceMetrics):
        """Log performance metrics to file."""
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metrics.to_dict()) + '\n')
        
        self.metrics_buffer.append(metrics)
        self._check_alerts(metrics)
    
    def _check_alerts(self, metrics: PerformanceMetrics):
        """Check for alert conditions."""
        alerts = []
        
        if abs(metrics.drawdown) > self.alert_thresholds['max_drawdown']:
            alerts.append(f"HIGH DRAWDOWN: {metrics.drawdown:.2%}")
        
        if abs(metrics.inventory) > self.alert_thresholds['max_inventory']:
            alerts.append(f"EXCESSIVE INVENTORY: {metrics.inventory}")
        
        if metrics.sharpe_ratio < self.alert_thresholds['min_sharpe']:
            alerts.append(f"LOW SHARPE: {metrics.sharpe_ratio:.3f}")
        
        if metrics.latency_ms > self.alert_thresholds['max_latency_ms']:
            alerts.append(f"HIGH LATENCY: {metrics.latency_ms:.1f}ms")
        
        for alert in alerts:
            self.logger.warning(f"⚠️  ALERT: {alert}")
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics from metrics buffer."""
        if not self.metrics_buffer:
            return {}
        
        pnls = [m.pnl for m in self.metrics_buffer]
        inventories = [m.inventory for m in self.metrics_buffer]
        latencies = [m.latency_ms for m in self.metrics_buffer]
        
        return {
            'uptime_seconds': time.time() - self.start_time,
            'total_metrics': len(self.metrics_buffer),
            'avg_pnl': np.mean(pnls),
            'std_pnl': np.std(pnls),
            'avg_inventory': np.mean(np.abs(inventories)),
            'max_inventory': np.max(np.abs(inventories)),
            'avg_latency_ms': np.mean(latencies),
            'max_latency_ms': np.max(latencies),
            'last_update': datetime.now().isoformat()
        }
    
    def log_event(self, event_type: str, message: str, level: str = 'INFO'):
        """Log an application event."""
        log_method = getattr(self.logger, level.lower())
        log_method(f"[{event_type}] {message}")
    
    def log_error(self, error: Exception, context: Optional[Dict] = None):
        """Log an error with context."""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {}
        }
        
        self.logger.error(f"ERROR: {json.dumps(error_data)}")
        
        # Write to error log
        with open(self.log_dir / 'errors.jsonl', 'a') as f:
            f.write(json.dumps(error_data) + '\n')
    
    def export_metrics(self, output_file: Optional[str] = None) -> str:
        """Export metrics to CSV."""
        import pandas as pd
        
        if not self.metrics_buffer:
            return ""
        
        df = pd.DataFrame([m.to_dict() for m in self.metrics_buffer])
        
        output_file = output_file or str(self.log_dir / f"metrics_{datetime.now():%Y%m%d_%H%M%S}.csv")
        df.to_csv(output_file, index=False)
        
        self.logger.info(f"Exported metrics to {output_file}")
        return output_file
    
    def clear_buffer(self):
        """Clear metrics buffer (after export)."""
        self.metrics_buffer = []


class HealthCheck:
    """System health monitoring."""
    
    def __init__(self):
        self.checks = {}
    
    def register_check(self, name: str, check_func):
        """Register a health check function."""
        self.checks[name] = check_func
    
    def run_checks(self) -> Dict[str, bool]:
        """Run all health checks."""
        results = {}
        for name, check_func in self.checks.items():
            try:
                results[name] = check_func()
            except Exception as e:
                results[name] = False
                results[f"{name}_error"] = str(e)
        return results
    
    def is_healthy(self) -> bool:
        """Check if system is healthy."""
        results = self.run_checks()
        return all(v for k, v in results.items() if not k.endswith('_error'))


class AlertManager:
    """Manage and dispatch alerts."""
    
    def __init__(self, monitoring: MonitoringSystem):
        self.monitoring = monitoring
        self.alert_handlers = []
    
    def add_handler(self, handler):
        """Add an alert handler."""
        self.alert_handlers.append(handler)
    
    def send_alert(self, severity: str, message: str, details: Optional[Dict] = None):
        """Send an alert through all handlers."""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'severity': severity,
            'message': message,
            'details': details or {}
        }
        
        self.monitoring.log_event('ALERT', f"{severity}: {message}", level='WARNING')
        
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.monitoring.log_error(e, context={'alert': alert})


class ConsoleAlertHandler:
    """Print alerts to console."""
    
    def __call__(self, alert: Dict):
        severity_emoji = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'ERROR': '❌',
            'CRITICAL': '🚨'
        }
        emoji = severity_emoji.get(alert['severity'], '📢')
        print(f"\n{emoji} [{alert['severity']}] {alert['message']}")
        if alert['details']:
            print(f"   Details: {alert['details']}")


class FileAlertHandler:
    """Write alerts to file."""
    
    def __init__(self, alert_file: str = "logs/alerts.jsonl"):
        self.alert_file = Path(alert_file)
        self.alert_file.parent.mkdir(exist_ok=True)
    
    def __call__(self, alert: Dict):
        with open(self.alert_file, 'a') as f:
            f.write(json.dumps(alert) + '\n')


# Global monitoring instance
_monitor = None

def get_monitor(log_dir: str = "logs") -> MonitoringSystem:
    """Get or create global monitoring instance."""
    global _monitor
    if _monitor is None:
        _monitor = MonitoringSystem(log_dir=log_dir)
    return _monitor
