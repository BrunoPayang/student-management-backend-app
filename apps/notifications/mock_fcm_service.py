class MockFCMService:
    """Mock FCM service for development/testing (free alternative to Firebase Cloud Messaging)"""
    
    def __init__(self):
        print("📱 Mock FCM Service initialized - notifications will be logged locally")
    
    def send_to_token(self, token: str, title: str, body: str, data: dict = None) -> bool:
        """Mock sending FCM notification to token"""
        print(f"📱 [MOCK FCM] Sending to token: {token[:20]}...")
        print(f"   Title: {title}")
        print(f"   Body: {body}")
        print(f"   Data: {data}")
        print(f"   Status: ✅ Delivered (mock)")
        return True
    
    def send_to_topic(self, topic: str, title: str, body: str, data: dict = None) -> bool:
        """Mock sending FCM notification to topic"""
        print(f"📱 [MOCK FCM] Sending to topic: {topic}")
        print(f"   Title: {title}")
        print(f"   Body: {body}")
        print(f"   Data: {data}")
        print(f"   Status: ✅ Delivered to topic (mock)")
        return True
    
    def get_service_type(self) -> str:
        """Get service type"""
        return "mock"
