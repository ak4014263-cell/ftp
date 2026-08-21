"""
Rate limiter to prevent IP blocking on VPS
Implements human-like request patterns
"""

import asyncio
import random
from datetime import datetime, timedelta
from collections import deque
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter that prevents IP blocking by:
    1. Limiting requests per hour
    2. Adding random delays between requests
    3. Implementing exponential backoff on errors
    """
    
    def __init__(
        self,
        requests_per_hour: int = 30,
        min_delay_seconds: float = 5.0,
        max_delay_seconds: float = 15.0,
        burst_size: int = 3
    ):
        """
        Initialize rate limiter
        
        Args:
            requests_per_hour: Maximum requests per hour (default: 30)
            min_delay_seconds: Minimum delay between requests (default: 5s)
            max_delay_seconds: Maximum delay between requests (default: 15s)
            burst_size: Allow this many requests without delay (default: 3)
        """
        self.requests_per_hour = requests_per_hour
        self.min_delay = min_delay_seconds
        self.max_delay = max_delay_seconds
        self.burst_size = burst_size
        
        self.request_times = deque()
        self.consecutive_errors = 0
        self.last_request_time: Optional[datetime] = None
        
    async def acquire(self):
        """
        Wait if necessary to stay under rate limit
        Call this before making any request
        """
        now = datetime.now()
        
        # Remove requests older than 1 hour
        while self.request_times and self.request_times[0] < now - timedelta(hours=1):
            self.request_times.popleft()
        
        # Check if we've exceeded hourly limit
        if len(self.request_times) >= self.requests_per_hour:
            oldest = self.request_times[0]
            wait_until = oldest + timedelta(hours=1)
            wait_seconds = (wait_until - now).total_seconds()
            
            if wait_seconds > 0:
                logger.warning(
                    f"⏱️  Rate limit reached ({self.requests_per_hour}/hour). "
                    f"Waiting {wait_seconds:.0f}s..."
                )
                await asyncio.sleep(wait_seconds)
                now = datetime.now()
        
        # Implement minimum delay between requests (unless in burst)
        if self.last_request_time and len(self.request_times) % self.burst_size != 0:
            elapsed = (now - self.last_request_time).total_seconds()
            
            # Calculate delay (longer if we've had errors)
            base_delay = random.uniform(self.min_delay, self.max_delay)
            error_multiplier = min(2 ** self.consecutive_errors, 8)  # Max 8x
            delay = base_delay * error_multiplier
            
            if elapsed < delay:
                wait_time = delay - elapsed
                logger.debug(f"⏱️  Delaying {wait_time:.1f}s (human-like behavior)")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_times.append(datetime.now())
        self.last_request_time = datetime.now()
    
    def record_success(self):
        """Call this after successful request"""
        self.consecutive_errors = 0
        logger.debug("✅ Request successful, error counter reset")
    
    def record_error(self):
        """Call this after failed request (especially 429, 403)"""
        self.consecutive_errors += 1
        logger.warning(
            f"❌ Request failed ({self.consecutive_errors} consecutive errors). "
            f"Next delay will be {2 ** self.consecutive_errors}x longer"
        )
    
    def get_stats(self) -> dict:
        """Get current rate limiter statistics"""
        now = datetime.now()
        recent_requests = [
            req for req in self.request_times 
            if req > now - timedelta(hours=1)
        ]
        
        return {
            "requests_last_hour": len(recent_requests),
            "requests_per_hour_limit": self.requests_per_hour,
            "utilization_percent": (len(recent_requests) / self.requests_per_hour) * 100,
            "consecutive_errors": self.consecutive_errors,
            "last_request": self.last_request_time.isoformat() if self.last_request_time else None
        }


class AdaptiveRateLimiter(RateLimiter):
    """
    Advanced rate limiter that adapts based on response patterns
    Automatically reduces rate if blocking is detected
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.original_limit = self.requests_per_hour
        self.blocked_count = 0
        self.success_count = 0
        
    def record_success(self):
        """Track successes and gradually increase rate"""
        super().record_success()
        self.success_count += 1
        self.blocked_count = 0
        
        # After 20 consecutive successes, try increasing rate slightly
        if self.success_count >= 20 and self.requests_per_hour < self.original_limit:
            old_limit = self.requests_per_hour
            self.requests_per_hour = min(
                self.requests_per_hour + 5,
                self.original_limit
            )
            if self.requests_per_hour != old_limit:
                logger.info(
                    f"📈 Rate limit increased: {old_limit} → {self.requests_per_hour} req/hour "
                    f"(after {self.success_count} successes)"
                )
            self.success_count = 0
    
    def record_error(self, is_blocking=False):
        """Track errors and reduce rate if blocked"""
        super().record_error()
        
        if is_blocking:
            self.blocked_count += 1
            self.success_count = 0
            
            # Reduce rate after being blocked
            if self.blocked_count >= 2:
                old_limit = self.requests_per_hour
                self.requests_per_hour = max(
                    self.requests_per_hour // 2,
                    5  # Minimum 5 requests/hour
                )
                logger.warning(
                    f"📉 Rate limit reduced due to blocking: {old_limit} → {self.requests_per_hour} req/hour"
                )
                self.blocked_count = 0
    
    def get_stats(self) -> dict:
        """Get enhanced statistics"""
        stats = super().get_stats()
        stats.update({
            "adaptive": True,
            "original_limit": self.original_limit,
            "current_limit": self.requests_per_hour,
            "success_streak": self.success_count,
            "blocked_count": self.blocked_count
        })
        return stats


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(
    requests_per_hour: int = 30,
    adaptive: bool = True
) -> RateLimiter:
    """
    Get global rate limiter instance (singleton pattern)
    
    Args:
        requests_per_hour: Maximum requests per hour
        adaptive: Use adaptive rate limiter (adjusts based on blocks)
    
    Returns:
        RateLimiter instance
    """
    global _rate_limiter
    
    if _rate_limiter is None:
        if adaptive:
            _rate_limiter = AdaptiveRateLimiter(requests_per_hour=requests_per_hour)
        else:
            _rate_limiter = RateLimiter(requests_per_hour=requests_per_hour)
        
        logger.info(
            f"🔧 Rate limiter initialized: {requests_per_hour} req/hour "
            f"({'adaptive' if adaptive else 'fixed'})"
        )
    
    return _rate_limiter
