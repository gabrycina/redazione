WELCOME_EMAIL = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                font-family: Arial, sans-serif;
                line-height: 1.6;
            }}
            .highlight {{
                background-color: #f0f0f0;
                padding: 0 4px;
            }}
            .cta-button {{
                display: inline-block;
                padding: 10px 20px;
                background-color: #f0f0f0;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <h2>Welcome to Redact!</h2>
            
            <p>We're excited to have you on board. To complete your Redact account setup, please follow our <span class="highlight">✨ simple onboarding ✨</span>:</p>
            
            <ol>
                <li><strong>Complete Onboarding:</strong> After clicking the link, you'll be guided through a quick onboarding process where you'll:
                    <ul>
                        <li>Set up your <strong>Sources List</strong> (links to information sources)</li>
                        <li>Define your <strong>Preferences Prompt</strong> (keywords, topics, etc.)</li>
                    </ul>
                </li>
            </ol>
            
            <p>Don't worry if you're not sure what to choose – we have starter configurations available during onboarding to help you get started quickly!</p>
            
            <a href="https://redact.lofipapers.com/signup/{subscription_code}" class="cta-button">Confirm Email & Start Onboarding</a>
            
            <p>This link will expire in 24 hours for security reasons. If you need a new link, please visit our website and request a new confirmation email.</p>
            
            <p>We're looking forward to personalizing your Redact experience!</p>
            
            <p>Best regards,</p>
            
            <p>The Redact Team 💌<br>
            <a href="https://redact.lofipapers.com">redact.lofipapers.com</a></p>
        </div>
    </body>
    </html>
"""

EMAIL_BODY = """
<!doctype html>
<html lang="en">
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>Daily Redact</title>
    <style media="all" type="text/css">
    /* -------------------------------------
    GLOBAL RESETS
------------------------------------- */
    
    body {{
      font-family: Helvetica, sans-serif;
      -webkit-font-smoothing: antialiased;
      font-size: 16px;
      line-height: 1.3;
      -ms-text-size-adjust: 100%;
      -webkit-text-size-adjust: 100%;
    }}
    
    table {{
      border-collapse: separate;
      mso-table-lspace: 0pt;
      mso-table-rspace: 0pt;
      width: 100%;
    }}
    
    table td {{
      font-family: Helvetica, sans-serif;
      font-size: 16px;
      vertical-align: top;
    }}
    /* -------------------------------------
    BODY & CONTAINER
------------------------------------- */
    
    body {{
      background-color: #f4f5f6;
      margin: 0;
      padding: 0;
    }}
    
    .body {{
      background-color: #f4f5f6;
      width: 100%;
    }}
    
    .container {{
      margin: 0 auto !important;
      max-width: 600px;
      padding: 0;
      padding-top: 24px;
      width: 600px;
    }}
    
    .content {{
      box-sizing: border-box;
      display: block;
      margin: 0 auto;
      max-width: 600px;
      padding: 0;
    }}
    /* -------------------------------------
    HEADER, FOOTER, MAIN
------------------------------------- */
    
    .main {{
      background: #ffffff;
      border: 1px solid #eaebed;
      border-radius: 16px;
      width: 100%;
    }}
    
    .wrapper {{
      box-sizing: border-box;
      padding: 24px;
    }}
    
    .footer {{
      clear: both;
      padding-top: 24px;
      text-align: center;
      width: 100%;
    }}
    
    .footer td,
    .footer p,
    .footer span,
    .footer a {{
      color: #9a9ea6;
      font-size: 16px;
      text-align: center;
    }}
    /* -------------------------------------
    TYPOGRAPHY
------------------------------------- */
    
    p {{
      font-family: Helvetica, sans-serif;
      font-size: 16px;
      font-weight: normal;
      margin: 0;
      margin-bottom: 16px;
    }}
    
    a {{
      color: #0867ec;
      text-decoration: underline;
    }}
    /* -------------------------------------
    BUTTONS
------------------------------------- */
    
    .btn {{
      box-sizing: border-box;
      min-width: 100% !important;
      width: 100%;
    }}
    
    .btn > tbody > tr > td {{
      padding-bottom: 16px;
    }}
    
    .btn table {{
      width: auto;
    }}
    
    .btn table td {{
      background-color: #ffffff;
      border-radius: 4px;
      text-align: center;
    }}
    
    .btn a {{
      background-color: #ffffff;
      border: solid 2px #0867ec;
      border-radius: 4px;
      box-sizing: border-box;
      color: #0867ec;
      cursor: pointer;
      display: inline-block;
      font-size: 16px;
      font-weight: bold;
      margin: 0;
      padding: 12px 24px;
      text-decoration: none;
      text-transform: capitalize;
    }}
    
    .btn-primary table td {{
      background-color: #0867ec;
    }}
    
    .btn-primary a {{
      background-color: #0867ec;
      border-color: #0867ec;
      color: #ffffff;
    }}
    
    @media all {{
      .btn-primary table td:hover {{
        background-color: #ec0867 !important;
      }}
      .btn-primary a:hover {{
        background-color: #ec0867 !important;
        border-color: #ec0867 !important;
      }}
    }}
    
    /* -------------------------------------
    OTHER STYLES THAT MIGHT BE USEFUL
------------------------------------- */
    
    .last {{
      margin-bottom: 0;
    }}
    
    .first {{
      margin-top: 0;
    }}
    
    .align-center {{
      text-align: center;
    }}
    
    .align-right {{
      text-align: right;
    }}
    
    .align-left {{
      text-align: left;
    }}
    
    .text-link {{
      color: #0867ec !important;
      text-decoration: underline !important;
    }}
    
    .clear {{
      clear: both;
    }}
    
    .mt0 {{
      margin-top: 0;
    }}
    
    .mb0 {{
      margin-bottom: 0;
    }}
    
    .preheader {{
      color: transparent;
      display: none;
      height: 0;
      max-height: 0;
      max-width: 0;
      opacity: 0;
      overflow: hidden;
      mso-hide: all;
      visibility: hidden;
      width: 0;
    }}
    
    .powered-by a {{
      text-decoration: none;
    }}
    
    /* -------------------------------------
    RESPONSIVE AND MOBILE FRIENDLY STYLES
------------------------------------- */
    
    @media only screen and (max-width: 640px) {{
      .main p,
      .main td,
      .main span {{
        font-size: 16px !important;
      }}
      .wrapper {{
        padding: 8px !important;
      }}
      .content {{
        padding: 0 !important;
      }}
      .container {{
        padding: 0 !important;
        padding-top: 8px !important;
        width: 100% !important;
      }}
      .main {{
        border-left-width: 0 !important;
        border-radius: 0 !important;
        border-right-width: 0 !important;
      }}
      .btn table {{
        max-width: 100% !important;
        width: 100% !important;
      }}
      .btn a {{
        font-size: 16px !important;
        max-width: 100% !important;
        width: 100% !important;
      }}
    }}
    /* -------------------------------------
    PRESERVE THESE STYLES IN THE HEAD
------------------------------------- */
    
    @media all {{
      .ExternalClass {{
        width: 100%;
      }}
      .ExternalClass,
      .ExternalClass p,
      .ExternalClass span,
      .ExternalClass font,
      .ExternalClass td,
      .ExternalClass div {{
        line-height: 100%;
      }}
      .apple-link a {{
        color: inherit !important;
        font-family: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
        text-decoration: none !important;
      }}
      #MessageViewBody a {{
        color: inherit;
        text-decoration: none;
        font-size: inherit;
        font-family: inherit;
        font-weight: inherit;
        line-height: inherit;
      }}
    }}
    </style>
  </head>
  <body>
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
      <tr>
        <td>&nbsp;</td>
        <td class="container">
          <div class="content">

            <!-- START CENTERED WHITE CONTAINER -->
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="main">

              <!-- START MAIN CONTENT AREA -->
              <tr>
                <td class="wrapper">
                  <h1>Daily Redact 🚀</h1>

                  <!-- For each article... -->
                  {}
                  

                </td>
              </tr>

              <!-- END MAIN CONTENT AREA -->
              </table>

            <!-- START FOOTER -->
            <div class="footer">
              <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td class="content-block">
                    <span class="apple-link">
                      Have some feedback or want to make adjustments? Reply to this email!
                    </span>
                    <br> Redact's Team 📪.
                  </td>
                </tr>
              </table>
            </div>

            <!-- END FOOTER -->
            
<!-- END CENTERED WHITE CONTAINER --></div>
        </td>
        <td>&nbsp;</td>
      </tr>
    </table>
  </body>
</html>
"""

EMAIL_ARTICLE = """
<div class="mt-3">
    <a class="font-bold" href="{}">
        <h3>{}</h3>
    </a>
    <div>{}</div>
</div>
"""
