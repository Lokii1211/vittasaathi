# Services module for VittaSaathi
from .nlp_service import NLPService, nlp_service
from .document_processor import DocumentProcessor, document_processor
from .financial_advisor import FinancialAdvisor, financial_advisor
from .message_builder import MessageBuilder, message_builder
from .notification_service import NotificationService, notification_service
from .voice_service import VoiceService, voice_service
from .dashboard_service import DashboardService, dashboard_service
from .advanced_features import (
    GamificationService, gamification_service,
    SmartInsightsService, smart_insights,
    SmartReplyService, smart_reply_service
)
