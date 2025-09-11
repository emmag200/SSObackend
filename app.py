from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import base64
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["*"])  # allows Netlify site to make requests to this backend

# Email configuration - these will be set as environment variables
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', 'dambustercalcs@gmail.com')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')  # App password, not regular password
COMPANY_EMAIL = os.environ.get('COMPANY_EMAIL', 'dambustercalcs@gmail.com')

def send_sso_report_email(customer_email, pdf_data, project_info):
    """
    Send SSO report email with PDF attachment
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = customer_email
        msg['Bcc'] = COMPANY_EMAIL  # BCC company email
        msg['Subject'] = "Dam Buster SSO Report"

        # Create email body
        job_number = project_info.get('jobNumber', 'N/A')
        project_name = project_info.get('projectName', 'N/A')
        sump_label = project_info.get('sumpLabel', 'SSO Device')
        total_flow = project_info.get('totalFlowRate', 'N/A')
        sso_size = project_info.get('ssoSize', 'N/A')
        sod_size = project_info.get('sodSize', 'N/A')

        # HTML email body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #e53e3e 0%, #d32f2f 100%); color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <h2 style="margin: 0; font-size: 24px;">Dam Buster</h2>
                    <p style="margin: 5px 0 0 0; font-size: 16px;">SSO Calculator Report</p>
                </div>
                
                <p>Dear Customer,</p>
                
                <p>Please find attached your Dam Buster SSO Calculator report with the following details:</p>
                
                <div style="background: #f8f9ff; padding: 15px; border-radius: 8px; margin: 15px 0;">
                    <h3 style="color: #e53e3e; margin-top: 0;">Project Summary</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 5px 0; font-weight: bold;">Job Number:</td>
                            <td style="padding: 5px 0;">{job_number}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; font-weight: bold;">Project Name:</td>
                            <td style="padding: 5px 0;">{project_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; font-weight: bold;">Device:</td>
                            <td style="padding: 5px 0;">{sump_label}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; font-weight: bold;">Total Flow Rate:</td>
                            <td style="padding: 5px 0;">{total_flow}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; font-weight: bold;">Recommended SSO:</td>
                            <td style="padding: 5px 0; color: #e53e3e; font-weight: bold;">{sso_size}</td>
                        </tr>
                        <tr>
                            <td style="padding: 5px 0; font-weight: bold;">Recommended SOD:</td>
                            <td style="padding: 5px 0; color: #e53e3e; font-weight: bold;">{sod_size}</td>
                        </tr>
                    </table>
                </div>
                
                <p>The attached PDF contains comprehensive calculation details, dimensions, and specifications for your project.</p>
                
                <p>If you have any questions about these calculations or need assistance with your Dam Buster products, please don't hesitate to contact us.</p>
                
                <div style="margin-top: 30px; padding: 15px; background: #f0f0f0; border-radius: 8px;">
                    <p style="margin: 0;"><strong>Dam Buster</strong></p>
                    <p style="margin: 5px 0 0 0; font-size: 14px; color: #666;">
                        Email: {EMAIL_ADDRESS}<br>
                        Website: www.dambuster.com.au
                    </p>
                </div>
                
                <p style="font-size: 12px; color: #888; margin-top: 20px;">
                    This report was generated on {datetime.now().strftime('%d/%m/%Y at %I:%M %p')} using the Dam Buster SSO Calculator.
                </p>
            </div>
        </body>
        </html>
        """

        # Plain text version
        text_body = f"""
Dear Customer,

Please find attached your Dam Buster SSO Calculator report with the following details:

Project Summary:
- Job Number: {job_number}
- Project Name: {project_name}  
- Device: {sump_label}
- Total Flow Rate: {total_flow}
- Recommended SSO: {sso_size}
- Recommended SOD: {sod_size}

The attached PDF contains comprehensive calculation details, dimensions, and specifications for your project.

If you have any questions about these calculations or need assistance with your Dam Buster products, please don't hesitate to contact us.

Best regards,
Dam Buster
Email: {EMAIL_ADDRESS}
Website: www.dambuster.com.au

This report was generated on {datetime.now().strftime('%d/%m/%Y at %I:%M %p')} using the Dam Buster SSO Calculator.
        """

        # Attach both HTML and plain text
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        # Attach PDF
        pdf_attachment = MIMEApplication(pdf_data, _subtype='pdf')
        pdf_filename = f"Dam_Buster_SSO_Report_{job_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
        if job_number == 'N/A':
            pdf_filename = f"Dam_Buster_SSO_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
        msg.attach(pdf_attachment)

        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        # Send to customer and BCC company
        recipients = [customer_email, COMPANY_EMAIL]
        server.send_message(msg, to_addrs=recipients)
        server.quit()

        return True

    except Exception as e:
        print(f"Email sending error: {str(e)}")
        return False

@app.route('/send-sso-report', methods=['POST'])
def send_sso_report():
    """
    Endpoint to receive PDF and send email
    """
    try:
        # Get data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data received'})

        # Validate required fields
        customer_email = data.get('customerEmail')
        pdf_base64 = data.get('pdfData')
        project_info = data.get('projectInfo', {})

        if not customer_email or not pdf_base64:
            return jsonify({'success': False, 'error': 'Missing email address or PDF data'})

        # Basic email validation
        if '@' not in customer_email or '.' not in customer_email:
            return jsonify({'success': False, 'error': 'Invalid email address format'})

        # Decode PDF data
        try:
            pdf_data = base64.b64decode(pdf_base64)
        except Exception as e:
            return jsonify({'success': False, 'error': 'Invalid PDF data format'})

        # Send email
        success = send_sso_report_email(customer_email, pdf_data, project_info)

        if success:
            return jsonify({
                'success': True, 
                'message': f'Report successfully sent to {customer_email}'
            })
        else:
            return jsonify({
                'success': False, 
                'error': 'Failed to send email. Please try again.'
            })

    except Exception as e:
        print(f"Error in send_sso_report: {str(e)}")
        return jsonify({'success': False, 'error': 'Server error occurred'})

@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint
    """
    return jsonify({'status': 'healthy', 'service': 'Dam Buster SSO Email Service'})

@app.route('/', methods=['GET'])
def home():
    """
    Basic home endpoint
    """
    return jsonify({
        'service': 'Dam Buster SSO Email Service',
        'status': 'running',
        'endpoints': {
            'send_report': '/send-sso-report (POST)',
            'health_check': '/health (GET)'
        }
    })

if __name__ == '__main__':
    # Check if required environment variables are set
    if not EMAIL_PASSWORD:
        print("WARNING: EMAIL_PASSWORD environment variable not set")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
