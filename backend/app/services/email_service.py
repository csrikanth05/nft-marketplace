import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging
from ..config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_user = getattr(settings, 'SMTP_USER', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.from_email = getattr(settings, 'FROM_EMAIL', self.smtp_user)
        
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send an email using SMTP"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured. Email not sent.")
            return False
            
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.from_email
            message['To'] = to_email
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(message)
                
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_nft_minted_email(
        self,
        to_email: str,
        username: str,
        nft_name: str,
        token_id: int,
        contract_address: str,
        tx_hash: Optional[str] = None
    ) -> bool:
        """Send NFT minted notification email"""
        
        subject = f"🎉 NFT Minted Successfully - {nft_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .nft-details {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .detail-row {{
                    padding: 10px 0;
                    border-bottom: 1px solid #eee;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #667eea;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Congratulations!</h1>
                    <p>Your NFT has been successfully minted</p>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Great news! Your NFT has been successfully minted on the blockchain.</p>
                    
                    <div class="nft-details">
                        <h3>NFT Details</h3>
                        <div class="detail-row">
                            <span class="detail-label">Name:</span> {nft_name}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Token ID:</span> {token_id}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Contract:</span> {contract_address[:10]}...{contract_address[-8:]}
                        </div>
                        {f'<div class="detail-row"><span class="detail-label">Transaction:</span> {tx_hash[:10]}...{tx_hash[-8:]}</div>' if tx_hash else ''}
                    </div>
                    
                    <p>You can now view, list, or transfer your NFT from your collection.</p>
                    
                    <center>
                        <a href="http://localhost:5173/my-nfts" class="button">View My NFTs</a>
                    </center>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        Happy collecting!<br>
                        <strong>NFT Marketplace Team</strong>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)


# Singleton instance
email_service = EmailService()
