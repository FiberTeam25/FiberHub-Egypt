"""
All SQLAlchemy models are imported here so Alembic can discover them.
"""

from app.models.user import User, EmailVerificationToken, PasswordResetToken, RefreshToken  # noqa: F401
from app.models.company import Company, CompanyMember  # noqa: F401
from app.models.profile import IndividualProfile  # noqa: F401
from app.models.category import ProductCategory, ServiceCategory, Governorate  # noqa: F401
from app.models.company import CompanyService, CompanyProduct  # noqa: F401
from app.models.company import Certification, ProjectReference, ProfileMedia  # noqa: F401
from app.models.verification import VerificationRequest, VerificationDocument  # noqa: F401
from app.models.rfq import RFQ, RFQAttachment, RFQInvitation, RFQResponse, RFQStatusHistory  # noqa: F401
from app.models.message import MessageThread, MessageParticipant, Message, MessageAttachment  # noqa: F401
from app.models.review import Review, ReviewFlag  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.admin import AdminActionLog, Shortlist  # noqa: F401
