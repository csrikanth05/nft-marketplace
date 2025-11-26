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


    def send_nft_bought_email(
        self,
        to_email: str,
        username: str,
        nft_name: str,
        price_eth: float,
        tx_hash: str
    ) -> bool:
        """Send NFT bought notification email to buyer"""
        
        subject = f"🛍️ Purchase Successful - {nft_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .nft-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .detail-row {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
                .detail-label {{ font-weight: bold; color: #3b82f6; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Purchase Successful!</h1>
                    <p>You are now the owner of {nft_name}</p>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Your purchase was successful! The NFT has been transferred to your wallet.</p>
                    
                    <div class="nft-details">
                        <h3>Transaction Details</h3>
                        <div class="detail-row">
                            <span class="detail-label">NFT:</span> {nft_name}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Price:</span> {price_eth} ETH
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Transaction:</span> {tx_hash[:10]}...{tx_hash[-8:]}
                        </div>
                    </div>
                    
                    <center>
                        <a href="http://localhost:5173/my-nfts" class="button">View My NFTs</a>
                    </center>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        Thank you for using our marketplace!<br>
                        <strong>NFT Marketplace Team</strong>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return self._send_email(to_email, subject, html_content)

    def send_nft_sold_email(
        self,
        to_email: str,
        username: str,
        nft_name: str,
        price_eth: float,
        tx_hash: str
    ) -> bool:
        """Send NFT sold notification email to seller"""
        
        subject = f"💰 NFT Sold - {nft_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .nft-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .detail-row {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
                .detail-label {{ font-weight: bold; color: #10b981; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>NFT Sold!</h1>
                    <p>Your NFT has been sold</p>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Good news! Your NFT <strong>{nft_name}</strong> has been sold.</p>
                    
                    <div class="nft-details">
                        <h3>Sale Details</h3>
                        <div class="detail-row">
                            <span class="detail-label">NFT:</span> {nft_name}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Sale Price:</span> {price_eth} ETH
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Transaction:</span> {tx_hash[:10]}...{tx_hash[-8:]}
                        </div>
                    </div>
                    
                    <p>The funds (minus platform fees) have been transferred to your wallet.</p>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        Keep creating and listing!<br>
                        <strong>NFT Marketplace Team</strong>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return self._send_email(to_email, subject, html_content)

    def send_bid_placed_email(
        self,
        to_email: str,
        username: str,
        nft_name: str,
        bid_amount: float
    ) -> bool:
        """Send bid placed notification email to bidder"""
        
        subject = f"✅ Bid Placed - {nft_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .nft-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .detail-row {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
                .detail-label {{ font-weight: bold; color: #3b82f6; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Bid Placed Successfully!</h1>
                    <p>You have placed a bid on {nft_name}</p>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Your bid has been successfully placed on the blockchain.</p>
                    
                    <div class="nft-details">
                        <h3>Bid Details</h3>
                        <div class="detail-row">
                            <span class="detail-label">NFT:</span> {nft_name}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Bid Amount:</span> {bid_amount} ETH
                        </div>
                    </div>
                    
                    <p>We will notify you if you are outbid or if you win the auction.</p>
                    
                    <center>
                        <a href="http://localhost:5173/auctions" class="button">View Auctions</a>
                    </center>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        Good luck!<br>
                        <strong>NFT Marketplace Team</strong>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return self._send_email(to_email, subject, html_content)

    def send_outbid_email(
        self,
        to_email: str,
        username: str,
        nft_name: str,
        new_bid_amount: float
    ) -> bool:
        """Send outbid notification email to previous bidder"""
        
        subject = f"⚠️ You've been outbid - {nft_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .nft-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .detail-row {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
                .detail-label {{ font-weight: bold; color: #f59e0b; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #f59e0b; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>You've Been Outbid!</h1>
                    <p>Someone placed a higher bid on {nft_name}</p>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Another user has placed a higher bid on the NFT you were bidding on.</p>
                    
                    <div class="nft-details">
                        <h3>Auction Update</h3>
                        <div class="detail-row">
                            <span class="detail-label">NFT:</span> {nft_name}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">New Highest Bid:</span> {new_bid_amount} ETH
                        </div>
                    </div>
                    
                    <p>You can withdraw your previous bid funds from the auction page.</p>
                    
                    <center>
                        <a href="http://localhost:5173/auctions" class="button">Place New Bid</a>
                    </center>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        Don't give up yet!<br>
                        <strong>NFT Marketplace Team</strong>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return self._send_email(to_email, subject, html_content)

    def send_auction_won_email(
        self,
        to_email: str,
        username: str,
        nft_name: str,
        winning_bid: float,
        tx_hash: str
    ) -> bool:
        """Send auction won notification email to winner"""
        
        subject = f"🏆 You Won the Auction! - {nft_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .nft-details {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .detail-row {{ padding: 10px 0; border-bottom: 1px solid #eee; }}
                .detail-label {{ font-weight: bold; color: #10b981; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Congratulations!</h1>
                    <p>You won the auction for {nft_name}</p>
                </div>
                <div class="content">
                    <p>Hi {username},</p>
                    <p>Fantastic news! You have won the auction. The NFT has been transferred to your wallet.</p>
                    
                    <div class="nft-details">
                        <h3>Winning Details</h3>
                        <div class="detail-row">
                            <span class="detail-label">NFT:</span> {nft_name}
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Winning Bid:</span> {winning_bid} ETH
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Transaction:</span> {tx_hash[:10]}...{tx_hash[-8:]}
                        </div>
                    </div>
                    
                    <center>
                        <a href="http://localhost:5173/my-nfts" class="button">View My NFTs</a>
                    </center>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        Enjoy your new NFT!<br>
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
