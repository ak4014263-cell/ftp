#!/usr/bin/env python3
"""
Monitor IP health and detect if we're being blocked by WTTJ
Run this periodically via cron to get alerts when IP is blocked
"""

import asyncio
import httpx
import os
from datetime import datetime
from typing import Dict, List

class IPHealthMonitor:
    def __init__(self):
        self.test_urls = [
            "https://www.welcometothejungle.com",
            "https://www.welcometothejungle.com/en/jobs",
            "https://www.welcometothejungle.com/en/authenticate/signup"
        ]
        self.timeout = 15.0
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        
    async def check_url(self, url: str) -> Dict:
        """Check if a URL is accessible"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.user_agent},
                    follow_redirects=True
                )
                
                return {
                    "url": url,
                    "status_code": response.status_code,
                    "blocked": response.status_code in [403, 429],
                    "error": None,
                    "response_time": response.elapsed.total_seconds()
                }
        except httpx.TimeoutException:
            return {
                "url": url,
                "status_code": None,
                "blocked": True,
                "error": "Timeout",
                "response_time": None
            }
        except Exception as e:
            return {
                "url": url,
                "status_code": None,
                "blocked": False,
                "error": str(e),
                "response_time": None
            }
    
    async def check_all(self) -> List[Dict]:
        """Check all URLs"""
        tasks = [self.check_url(url) for url in self.test_urls]
        return await asyncio.gather(*tasks)
    
    def format_result(self, result: Dict) -> str:
        """Format a single result for logging"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        url = result["url"]
        
        if result["blocked"]:
            status = "🔴 BLOCKED"
            detail = f"Status: {result['status_code']}"
        elif result["error"]:
            status = "⚠️  ERROR"
            detail = f"Error: {result['error']}"
        elif result["status_code"] == 200:
            status = "✅ OK"
            detail = f"Response time: {result['response_time']:.2f}s"
        else:
            status = f"⚠️  {result['status_code']}"
            detail = ""
        
        return f"[{timestamp}] {status} - {url} - {detail}"
    
    async def send_alert(self, message: str):
        """Send alert via webhook or email"""
        # TODO: Implement your alerting system
        # Options:
        # 1. Slack webhook
        # 2. Discord webhook
        # 3. Email via SMTP
        # 4. Telegram bot
        # 5. SMS via Twilio
        
        print(f"🚨 ALERT: {message}")
        
        # Example: Slack webhook
        slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        if slack_webhook:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        slack_webhook,
                        json={"text": f"🚨 Swiply Alert: {message}"}
                    )
            except Exception as e:
                print(f"Failed to send Slack alert: {e}")
    
    async def run(self):
        """Run health check"""
        results = await self.check_all()
        
        # Log all results
        for result in results:
            print(self.format_result(result))
        
        # Check if any URLs are blocked
        blocked_urls = [r for r in results if r["blocked"]]
        
        if blocked_urls:
            blocked_count = len(blocked_urls)
            total_count = len(results)
            message = f"IP blocked on {blocked_count}/{total_count} URLs"
            await self.send_alert(message)
            
            # Log details
            print(f"\n⚠️  WARNING: {blocked_count} URLs are blocked!")
            for result in blocked_urls:
                print(f"   - {result['url']} (Status: {result['status_code']})")
            
            return False
        else:
            print(f"\n✅ All {len(results)} URLs are accessible")
            return True


async def main():
    """Main entry point"""
    monitor = IPHealthMonitor()
    
    print("🔍 Swiply IP Health Monitor")
    print("=" * 60)
    
    is_healthy = await monitor.run()
    
    print("=" * 60)
    
    # Exit with non-zero if blocked (useful for cron monitoring)
    exit(0 if is_healthy else 1)


if __name__ == "__main__":
    asyncio.run(main())
