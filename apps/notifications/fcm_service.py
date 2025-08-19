import firebase_admin
from firebase_admin import messaging
from django.conf import settings
import os

class FCMService:
    def __init__(self):
        self.use_mock = True  # Default to mock service
        self._initialize_firebase()

    def _initialize_firebase(self):
        try:
            cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
            if cred_path and os.path.exists(cred_path):
                if not firebase_admin._apps:
                    firebase_admin.initialize_app()
                self.use_mock = False
                print("✅ Firebase FCM initialized successfully")
            else:
                print("⚠️  Firebase credentials not found, using mock FCM service")
                self.use_mock = True
        except Exception as e:
            print(f"⚠️  Firebase FCM initialization error: {e}")
            print("🔄 Falling back to mock FCM service")
            self.use_mock = True

    def send_to_token(self, token: str, title: str, body: str, data: dict = None) -> bool:
        """Send FCM notification to token"""
        if self.use_mock:
            return self._mock_send_to_token(token, title, body, data)
        else:
            return self._firebase_send_to_token(token, title, body, data)

    def send_to_topic(self, topic: str, title: str, body: str, data: dict = None) -> bool:
        """Send FCM notification to topic"""
        if self.use_mock:
            return self._mock_send_to_topic(topic, title, body, data)
        else:
            return self._firebase_send_to_topic(topic, title, body, data)

    def _firebase_send_to_token(self, token: str, title: str, body: str, data: dict = None) -> bool:
        """Send via Firebase FCM"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                token=token
            )
            messaging.send(message)
            return True
        except Exception as e:
            print(f"FCM send error: {e}")
            return False

    def _firebase_send_to_topic(self, topic: str, title: str, body: str, data: dict = None) -> bool:
        """Send via Firebase FCM topic"""
        try:
            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                data=data or {},
                topic=topic
            )
            messaging.send(message)
            return True
        except Exception as e:
            print(f"FCM topic send error: {e}")
            return False

    def _mock_send_to_token(self, token: str, title: str, body: str, data: dict = None) -> bool:
        """Mock FCM send to token"""
        print(f"📱 [MOCK FCM] Sending to token: {token[:20]}...")
        print(f"   Title: {title}")
        print(f"   Body: {body}")
        print(f"   Data: {data}")
        print(f"   Status: ✅ Delivered (mock)")
        return True

    def _mock_send_to_topic(self, topic: str, title: str, body: str, data: dict = None) -> bool:
        """Mock FCM send to topic"""
        print(f"📱 [MOCK FCM] Sending to topic: {topic}")
        print(f"   Title: {title}")
        print(f"   Body: {body}")
        print(f"   Data: {data}")
        print(f"   Status: ✅ Delivered to topic (mock)")
        return True

    def get_service_type(self) -> str:
        """Get current service type"""
        return "mock" if self.use_mock else "firebase"
